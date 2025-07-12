"""search_engine.py — 柔軟検索エンジン
====================================
TM‑SONAR 相当の検索条件を解析し、安全な SQL とパラメータを生成するモジュール。

2025‑07‑09 パッチ内容
---------------------
* `_determine_match_type` を改良: 完全一致/前方/後方/部分/範囲 を正確判定
* `_normalize_value` を改良: "…" や * の除去ロジックを整理
* `_parse_advanced_conditions` を改良: AND/OR/NOT トグル & 行グループ化(`group`) に対応
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Enum 定義
# ─────────────────────────────────────────────
class MatchType(Enum):
    EXACT = "exact"
    PARTIAL = "partial"
    PREFIX = "prefix"
    SUFFIX = "suffix"
    RANGE = "range"
    IN = "in"  # 未使用だが拡張用

class LogicalOperator(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

# ─────────────────────────────────────────────
# データクラス
# ─────────────────────────────────────────────
@dataclass
class SearchCondition:
    field_name: str
    value: Union[str, List[str], Tuple[Any, Any]]
    match_type: MatchType = MatchType.PARTIAL
    is_negated: bool = False

    def to_sql(self, params: List[Any], alias: str = "") -> Tuple[str, List[Any]]:
        col = f"{alias}.{self.field_name}" if alias else self.field_name

        def _like(value: str, neg: bool = False):
            params.append(value)
            return f"{col} {'NOT ' if neg else ''}LIKE ?"

        if self.match_type == MatchType.EXACT:
            params.append(self.value)
            return f"{col} {'!=' if self.is_negated else '='} ?", params
        if self.match_type == MatchType.PARTIAL:
            return _like(f"%{self.value}%", self.is_negated), params
        if self.match_type == MatchType.PREFIX:
            return _like(f"{self.value}%", self.is_negated), params
        if self.match_type == MatchType.SUFFIX:
            return _like(f"%{self.value}", self.is_negated), params
        if self.match_type == MatchType.RANGE:
            start, end = self.value  # type: ignore[misc]
            params.extend([start, end])
            return (
                f"({col} < ? OR {col} > ?)" if self.is_negated else f"{col} BETWEEN ? AND ?",
                params,
            )
        if self.match_type == MatchType.IN:
            placeholders = ",".join("?" for _ in self.value)
            params.extend(self.value)  # type: ignore[arg-type]
            return (
                f"{col} NOT IN ({placeholders})" if self.is_negated else f"{col} IN ({placeholders})",
                params,
            )
        raise ValueError("Unsupported match type")

@dataclass
class ConditionGroup:
    conditions: List[Union["ConditionGroup", SearchCondition]] = field(default_factory=list)
    logical_operator: LogicalOperator = LogicalOperator.AND

    def add_condition(self, cond: Union["ConditionGroup", SearchCondition]):
        self.conditions.append(cond)

    def to_sql(self, params: List[Any], mapping: Dict[str, str]) -> Tuple[str, List[Any]]:
        if not self.conditions:
            return "1=1", params
        parts: List[str] = []
        for c in self.conditions:
            if isinstance(c, ConditionGroup):
                sql_part, params = c.to_sql(params, mapping)
            else:
                alias = mapping.get(c.field_name, "")
                sql_part, params = c.to_sql(params, alias)
            parts.append(f"({sql_part})" if isinstance(c, ConditionGroup) else sql_part)
        joined = f" {self.logical_operator.value} ".join(parts)
        return joined, params

# ─────────────────────────────────────────────
# クエリビルダー
# ─────────────────────────────────────────────
class SearchQueryBuilder:
    FIELD_TABLE_MAPPING: Dict[str, str] = {
        "normalized_app_num": "j",
        "standard_char_t": "s",
        "goods_classes": "gca",
        "designated_goods": "sg",
        "smlr_dsgn_group_cd": "tknd",
        "right_person_name": "h",
        "right_person_addr": "h",
        "shutugan_bi": "j",
        "reg_reg_ymd": "j",
        "dsgnt": "td",
        "reg_num": "r",
    }

    def __init__(self):
        self.base_table = "jiken_c_t j"
        self.joins: List[str] = []
        self.conditions = ConditionGroup()
        self.order_by: List[str] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None

    # ────────────────────────────────
    # 内部ユーティリティ
    # ────────────────────────────────
    def add_join(self, clause: str):
        if clause not in self.joins:
            self.joins.append(clause)

    # ────────────────────────────────
    # パラメータ解析
    # ────────────────────────────────
    def parse_search_params(self, p: Dict[str, Any]) -> "SearchQueryBuilder":
        if p.get("app_num"):
            self.conditions.add_condition(SearchCondition("normalized_app_num", p["app_num"].replace("-", ""), MatchType.EXACT))
        if p.get("mark_text"):
            self._add_mark_text_condition(p["mark_text"])
        if p.get("goods_classes"):
            self._add_goods_classes_condition(p["goods_classes"])
        if p.get("designated_goods"):
            self._add_designated_goods_condition(p["designated_goods"])
        if p.get("similar_group_codes"):
            self._add_similar_codes_condition(p["similar_group_codes"])
        if p.get("owner_name"):
            self._add_owner_condition(p["owner_name"])
        if p.get("app_date_from") or p.get("app_date_to"):
            self._add_date_range_condition("shutugan_bi", p.get("app_date_from"), p.get("app_date_to"))
        if p.get("reg_date_from") or p.get("reg_date_to"):
            self._add_date_range_condition("reg_reg_ymd", p.get("reg_date_from"), p.get("reg_date_to"))
        if p.get("advanced_conditions"):
            self._parse_advanced_conditions(p["advanced_conditions"])
        # sort/limit
        if p.get("sort_by"):
            self._add_sort_condition(p["sort_by"], p.get("sort_order", "ASC"))
        self.limit = int(p.get("limit", 0) or 0) or None
        self.offset = int(p.get("offset", 0) or 0) or None
        return self

    # ────────────────────────────────
    # マッチタイプ決定 (PATCH)
    # ────────────────────────────────
    def _determine_match_type(self, field_type: str, value: str) -> MatchType:
        # 日付系
        if field_type in {"110", "111"}:
            return MatchType.RANGE if ":" in value else MatchType.PREFIX
        # 完全一致 — "..."
        if value.startswith("\"") and value.endswith("\"") and len(value) > 2:
            return MatchType.EXACT
        # 前方一致 — 末尾 *
        if value.endswith("*") and not value.startswith("*"):
            return MatchType.PREFIX
        # 後方一致 — 先頭 *
        if value.startswith("*") and not value.endswith("*"):
            return MatchType.SUFFIX
        # 部分一致
        return MatchType.PARTIAL

    # 値の正規化 (PATCH)
    def _normalize_value(self, field_type: str, value: str) -> Union[str, Tuple[str, str]]:
        if value.startswith("\"") and value.endswith("\"") and len(value) > 2:
            value = value[1:-1]
        value = value.replace("*", "")
        if ":" in value and field_type in {"110", "111"}:
            a, b = value.split(":", 1)
            return a.replace("-", ""), b.replace("-", "")
        if field_type == "118":
            return value.replace("-", "")
        return value

    # ────────────────────────────────
    # 条件追加 helper（既存）
    # ────────────────────────────────
    def _add_mark_text_condition(self, text: str):
        self.add_join("LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num")
        self.conditions.add_condition(
            SearchCondition(
                "standard_char_t", self._normalize_value("101", text), self._determine_match_type("101", text)
            )
        )

    def _add_goods_classes_condition(self, cls_str: str):
        self.add_join(
            """
            LEFT JOIN (
                SELECT normalized_app_num, GROUP_CONCAT(DISTINCT goods_classes) AS concatenated_classes
                FROM goods_class_art GROUP BY normalized_app_num
            ) AS gca ON j.normalized_app_num = gca.normalized_app_num
            """
        )
        classes = [c.strip() for c in re.split(r"[ ,]", cls_str) if c.strip()]
        or_group = ConditionGroup(logical_operator=LogicalOperator.OR) if len(classes) > 1 else None
        for c in classes:
            cond = SearchCondition("concatenated_classes", c, MatchType.PARTIAL)
            (or_group or self.conditions).add_condition(cond)  # type: ignore[arg-type]
        if or_group:
            self.conditions.add_condition(or_group)

    def _add_designated_goods_condition(self, term: str):
        self.add_join(
            """
            LEFT JOIN (
                SELECT normalized_app_num, GROUP_CONCAT(DISTINCT designated_goods) AS concatenated_goods
                FROM jiken_c_t_shohin_joho GROUP BY normalized_app_num
            ) AS sg ON j.normalized_app_num = sg.normalized_app_num
            """
        )
        for t in term.split():
            self.conditions.add_condition(SearchCondition("concatenated_goods", t, MatchType.PARTIAL))

    def _add_similar_codes_condition(self, codes: str):
        self.add_join(
            """
            LEFT JOIN (
                SELECT normalized_app_num, GROUP_CONCAT(DISTINCT smlr_dsgn_group_cd) AS concatenated_codes
                FROM t_knd_info_art_table GROUP BY normalized_app_num
            ) AS tknd ON j.normalized_app_num = tknd.normalized_app_num
            """
        )
        items = [c.strip() for c in re.split(r"[ ,]", codes) if c.strip()]
        grp = ConditionGroup(logical_operator=LogicalOperator.OR) if len(items) > 1 else None
        for i in items:
            cond = SearchCondition("concatenated_codes", i, MatchType.PARTIAL)
            (grp or self.conditions).add_condition(cond)  # type: ignore[arg-type]
        if grp:
            self.conditions.add_condition(grp)

    def _add_owner_condition(self, name: str):
        self.add_join("LEFT JOIN reg_mapping r ON j.normalized_app_num = r.app_num")
        self.add_join("LEFT JOIN right_person_art_t h ON r.reg_num = h.reg_num")
        self.conditions.add_condition(SearchCondition("right_person_name", name, MatchType.PARTIAL))

    def _add_date_range_condition(self, field: str, frm: str | None, to: str | None):
        if frm and to:
            self.conditions.add_condition(SearchCondition(field, (frm.replace("-", ""), to.replace("-", "")), MatchType.RANGE))
        elif frm:
            self.conditions.add_condition(SearchCondition(field, frm.replace("-", ""), MatchType.PREFIX))
        elif to:
            self.conditions.add_condition(SearchCondition(field, (None, to.replace("-", "")), MatchType.RANGE))

    # ────────────────────────────────
    # 高度条件解析 (PATCH)
    # ────────────────────────────────
    def _parse_advanced_conditions(self, adv: List[Dict[str, Any]]):
        group_map: Dict[str, ConditionGroup] = {}
        for item in adv:
            f_type = str(item.get("type", ""))
            val = str(item.get("str", ""))
            logic = item.get("logic", "AND").upper()
            grp_id = item.get("group", "")
            if not f_type or not val:
                continue
            field = {
                "101": "standard_char_t",
                "102": "right_person_name",
                "106": "smlr_dsgn_group_cd",
                "107": "designated_goods",
                "110": "shutugan_bi",
                "111": "reg_reg_ymd",
                "118": "normalized_app_num",
                "119": "reg_num",
                "123": "dsgnt",
            }.get(f_type)
            if not field:
                continue
            mt = self._determine_match_type(f_type, val)
            norm_val = self._normalize_value(f_type, val)
            cond = SearchCondition(field, norm_val, mt, is_negated=(logic == "NOT"))
            # グループ処理
            target_group: ConditionGroup = self.conditions
            if grp_id:
                if grp_id not in group_map:
                    group_map[grp_id] = ConditionGroup(logical_operator=LogicalOperator.OR)
                    self.conditions.add_condition(group_map[grp_id])
                target_group = group_map[grp_id]
            if logic == "OR" and target_group.logical_operator is LogicalOperator.AND:
                # AND グループ内に OR を入れる場合は新しい OR グループを作る
                or_grp = ConditionGroup(logical_operator=LogicalOperator.OR)
                or_grp.add_condition(cond)
                target_group.add_condition(or_grp)
            else:
                target_group.add_condition(cond)

    # ────────────────────────────────
    # ソート
    # ────────────────────────────────
    def _add_sort_condition(self, key: str, order: str = "ASC"):
        field = {
            "app_num": "j.normalized_app_num",
            "app_date": "j.shutugan_bi",
            "reg_date": "j.reg_reg_ymd",
            "mark_text": "s.standard_char_t",
            "owner_name": "h.right_person_name",
        }.get(key)
        if field:
            self.order_by.append(f"{field} {'DESC' if order.upper() == 'DESC' else 'ASC'}")

    # ────────────────────────────────
    # SQL 生成
    # ────────────────────────────────
    def _from_clause(self) -> str:
        return " ".join(["FROM", self.base_table, *self.joins])

    def build_count_query(self) -> Tuple[str, List[Any]]:
        params: List[Any] = []
        where, params = self.conditions.to_sql(params, self.FIELD_TABLE_MAPPING)
        where_clause = f"WHERE {where}" if where != "1=1" else ""
        sql = f"SELECT COUNT(DISTINCT j.normalized_app_num) AS total {self._from_clause()} {where_clause}"
        return sql, params

    def build_search_query(self) -> Tuple[str, List[Any]]:
        params: List[Any] = []
        where, params = self.conditions.to_sql(params, self.FIELD_TABLE_MAPPING)
        where_clause = f"WHERE {where}" if where != "1=1" else ""
        order_clause = f"ORDER BY {', '.join(self.order_by)}" if self.order_by else "ORDER BY j.normalized_app_num"
        limit_clause = ""
        if self.limit:
            limit_clause = f" LIMIT {self.limit}"
            if self.offset:
                limit_clause += f" OFFSET {self.offset}"
        sql = (
            f"SELECT DISTINCT j.normalized_app_num {self._from_clause()} {where_clause} {order_clause}{limit_clause}"
        )
        return sql, params

    def build_detail_query(self, nums: List[str]) -> Tuple[str, List[Any]]:
        if not nums:
            return "", []
        ph = ",".join("?" for _ in nums)
        sql = (
            """
            SELECT j.normalized_app_num AS app_num,
                   s.standard_char_t   AS mark_text,
                   j.shutugan_bi       AS app_date,
                   j.reg_reg_ymd       AS reg_date,
                   r.reg_num           AS reg_no,
                   h.right_person_name AS owner_name,
                   h.right_person_addr AS owner_addr
            FROM jiken_c_t j
            LEFT JOIN standard_char_t_art s ON j.normalized_app_num = s.normalized_app_num
            LEFT JOIN reg_mapping r ON j.normalized_app_num = r.app_num
            LEFT JOIN right_person_art_t h ON r.reg_num = h.reg_num
            WHERE j.normalized_app_num IN (
            """ + ph + ") GROUP BY j.normalized_app_num ORDER BY j.normalized_app_num"
        )
        return sql, nums

# ─────────────────────────────────────────────
# 検索実行ヘルパ
# ─────────────────────────────────────────────

def execute_search(params: Dict[str, Any], db_path: str) -> Dict[str, Any]:
    """params を解析し、SQL とパラメータを返す（実際の DB 実行は呼び出し側）"""
    builder = SearchQueryBuilder().parse_search_params(params)
    count_sql, count_params = builder.build_count_query()
    search_sql, search_params = builder.build_search_query()
    return {
        "builder": builder,
        "count_sql": count_sql,
        "count_params": count_params,
        "search_sql": search_sql,
        "search_params": search_params,
    }
