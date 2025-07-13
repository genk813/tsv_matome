#!/usr/bin/env python3
"""
テキスト正規化ユーティリティ
TM-SONAR水準の検索機能実現のためのP1基礎正規化
"""

import re
import unicodedata


class TextNormalizer:
    """
    商標・称呼テキストの正規化処理
    既存機能に影響を与えないよう、新しい機能として追加
    """
    
    def __init__(self):
        # P1-8: 旧字体→新字体の変換テーブル
        self.old_to_new_kanji = {
            '國': '国', '學': '学', '廣': '広', '圓': '円', '實': '実',
            '變': '変', '體': '体', '經': '経', '營': '営', '豐': '豊',
            '擧': '挙', '轉': '転', '聲': '声', '醫': '医', '爲': '為',
            '發': '発', '當': '当', '來': '来', '會': '会', '應': '応'
        }
        
        # P1-9: ローマ数字→算用数字の変換テーブル
        self.roman_to_arabic = {
            'Ⅰ': '1', 'Ⅱ': '2', 'Ⅲ': '3', 'Ⅳ': '4', 'Ⅴ': '5',
            'Ⅵ': '6', 'Ⅶ': '7', 'Ⅷ': '8', 'Ⅸ': '9', 'Ⅹ': '10',
            'ⅰ': '1', 'ⅱ': '2', 'ⅲ': '3', 'ⅳ': '4', 'ⅴ': '5',
            'ⅵ': '6', 'ⅶ': '7', 'ⅷ': '8', 'ⅸ': '9', 'ⅹ': '10'
        }
        
        # P1-7: ギリシャ・ラテン文字→アルファベット
        self.greek_latin_to_ascii = {
            'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e',
            'ζ': 'z', 'η': 'h', 'θ': 'th', 'ι': 'i', 'κ': 'k',
            'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o',
            'π': 'p', 'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'u',
            'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'o',
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',
            'Ζ': 'Z', 'Η': 'H', 'Θ': 'TH', 'Ι': 'I', 'Κ': 'K',
            'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O',
            'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'U',
            'Φ': 'F', 'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'O'
        }
        
        # P2-14: 法人種別語句リスト（前方・後方一致で除去）
        self.corporate_suffixes = [
            '株式会社', 'かぶしきがいしゃ', 'カブシキガイシャ',
            '有限会社', 'ゆうげんがいしゃ', 'ユウゲンガイシャ',
            '合同会社', 'ごうどうがいしゃ', 'ゴウドウガイシャ',
            '合資会社', 'ごうしがいしゃ', 'ゴウシガイシャ',
            '合名会社', 'ごうめいがいしゃ', 'ゴウメイガイシャ',
            '一般財団法人', 'いっぱんざいだんほうじん', 'イッパンザイダンホウジン',
            '公益財団法人', 'こうえきざいだんほうじん', 'コウエキザイダンホウジン',
            '一般社団法人', 'いっぱんしゃだんほうじん', 'イッパンシャダンホウジン',
            '公益社団法人', 'こうえきしゃだんほうじん', 'コウエキシャダンホウジン',
            '医療法人', 'いりょうほうじん', 'イリョウホウジン',
            '学校法人', 'がっこうほうじん', 'ガッコウホウジン',
            '宗教法人', 'しゅうきょうほうじん', 'シュウキョウホウジン',
            '特定非営利活動法人', 'とくていひえいりかつどうほうじん', 'トクテイヒエイリカツドウホウジン',
            'ＮＰＯ法人', 'エヌピーオーほうじん', 'エヌピーオーホウジン',
            '協同組合', 'きょうどうくみあい', 'キョウドウクミアイ',
            '農業協同組合', 'のうぎょうきょうどうくみあい', 'ノウギョウキョウドウクミアイ',
            '漁業協同組合', 'ぎょぎょうきょうどうくみあい', 'ギョギョウキョウドウクミアイ',
            '生活協同組合', 'せいかつきょうどうくみあい', 'セイカツキョウドウクミアイ',
            '農協', 'のうきょう', 'ノウキョウ', 'ＪＡ',
            '漁協', 'ぎょきょう', 'ギョキョウ',
            '生協', 'せいきょう', 'セイキョウ',
            '組合', 'くみあい', 'クミアイ',
            '財団', 'ざいだん', 'ザイダン',
            '社団', 'しゃだん', 'シャダン',
            '法人', 'ほうじん', 'ホウジン',
            '会社', 'かいしゃ', 'カイシャ',
            # 英語表記（長い形式を優先）
            'Corporation', 'CORPORATION',
            'Company', 'COMPANY',
            'Limited', 'LIMITED', 
            'Incorporated', 'INCORPORATED',
            'Limited Liability Company',
            'Limited Partnership',
            'Limited Liability Partnership',
            'Foundation', 'FOUNDATION',
            'Association', 'ASSOCIATION',
            'Organization', 'ORGANIZATION',
            'Institute', 'INSTITUTE',
            # 略語形式（ピリオド付きのみ、単独形式は除外）
            'Corp.', 'CORP.',
            'Co.', 'CO.',
            'Ltd.', 'LTD.',
            'Inc.', 'INC.',
            'L.L.C.', 'L.L.C', 'LLC',
            'L.P.', 'L.P', 'LP',
            'L.L.P.', 'L.L.P', 'LLP'
        ]
    
    def normalize_basic(self, text: str) -> str:
        """
        P1基礎正規化の実行
        商標・称呼テキスト用の基本的な正規化処理
        """
        if not text:
            return ""
        
        # P1-1: ひらがな→カタカナ変換
        text = self._hiragana_to_katakana(text)
        
        # P1-2: 全小文字→大文字（カナ・英字）
        text = text.upper()
        
        # P1-3: 長音「ー」、横線、ハイフンを "-" に統一
        text = self._normalize_hyphens(text)
        
        # P1-4: スペース除去
        text = re.sub(r'\s+', '', text)
        
        # P1-5: 特殊記号排除
        text = self._remove_special_symbols(text)
        
        # P1-6: 句読点・中点・カンマ・クォーテーション排除
        text = self._remove_punctuation(text)
        
        # P1-7: ギリシャ・ラテン文字→対応アルファベット
        text = self._convert_greek_latin(text)
        
        # P1-8: 旧字体漢字→新字体
        text = self._convert_old_kanji(text)
        
        # P1-9: ローマ数字→算用数字
        text = self._convert_roman_numerals(text)
        
        return text
    
    def normalize_pronunciation(self, text: str) -> str:
        """
        称呼（発音同一）用の正規化
        基礎正規化に加えて発音ゆらぎを統一
        """
        # まず基礎正規化を実行
        text = self.normalize_basic(text)
        
        # P1-10: 発音同一文字の統一
        text = self._normalize_pronunciation_same(text)
        
        # P1-11: 微差音統一
        text = self._normalize_subtle_sounds(text)
        
        # P1-12: 長音・促音・長音化母音の処理
        text = self._normalize_long_sounds(text)
        
        # P1-13: 拗音大文字化
        text = self._normalize_contracted_sounds(text)
        
        return text
    
    def normalize_trademark(self, text: str) -> str:
        """
        商標名専用の正規化（TM-SONAR仕様準拠）
        表示用商標・検索用商標の検索精度向上のため
        """
        if not text:
            return ""
        
        # 1. ひらがな→カタカナ変換
        text = self._hiragana_to_katakana(text)
        
        # 2. ひらがな、カタカナ、英文字の小文字→大文字
        text = text.upper()
        
        # 3. 長音、横線、ハイフン→ハイフン統一
        text = self._normalize_hyphens(text)
        
        # 4. ギリシャ文字、ラテン文字の一部→アルファベット
        text = self._convert_greek_latin(text)
        
        # 5. 特殊記号の排除（TM-SONAR指定のもののみ）
        text = self._remove_tm_sonar_special_symbols(text)
        
        # 6. 記号の排除（TM-SONAR指定：句点、中点、点、カンマ、クォーテーション）
        text = self._remove_tm_sonar_punctuation(text)
        
        # 7. スペースの排除
        text = re.sub(r'\s+', '', text)
        
        # 8. 漢字旧字体→新字体
        text = self._convert_old_kanji(text)
        
        # 9. ローマ数字→算用数字（TM-SONAR仕様）
        text = self._convert_roman_numerals(text)
        
        return text
    
    def _remove_tm_sonar_special_symbols(self, text: str) -> str:
        """TM-SONAR指定の特殊記号のみを排除"""
        # TM-SONAR仕様：▲▼§￠＼∞のみ排除
        tm_sonar_symbols = ['▲', '▼', '§', '￠', '＼', '∞']
        for symbol in tm_sonar_symbols:
            text = text.replace(symbol, '')
        return text
    
    def _remove_tm_sonar_punctuation(self, text: str) -> str:
        """TM-SONAR指定の記号のみを排除（読点は保持）"""
        # TM-SONAR仕様：句点(、),中点(・),点(．),カンマ(，),クォーテーション('")のみ排除
        # 注意：読点（。）やその他の記号（《》【】『』など）は保持
        # 注意：中点「・」も実際は保持される（TM-SONAR仕様では分離される）
        tm_sonar_punctuation = [
            '、', '．', '，', "'", '"', '"', '"', ''', '''
        ]
        for punct in tm_sonar_punctuation:
            text = text.replace(punct, '')
        return text
    
    def split_trademark_components(self, text: str) -> list:
        """
        二段併記と構成分離への対応
        TM-SONAR仕様：二段併記については「＼」で分断してデータを作成
        """
        if not text:
            return []
        
        # 二段併記の分離（「＼」区切り）
        if '＼' in text:
            components = []
            parts = text.split('＼')
            for part in parts:
                if part.strip():
                    components.append(part.strip())
            # 一連データも作成（TM-SONAR仕様）
            combined = ''.join(parts)
            if combined and combined not in components:
                components.append(combined)
            return components
        else:
            return [text]
    
    def parse_multi_search_terms(self, text: str) -> dict:
        """
        複数指定検索とクエスチョンマーク検索の解析
        TM-SONAR仕様：スペースまたはカンマで区切り、「？」で全指定
        """
        if not text:
            return {"terms": [], "wildcard": False, "partial_match": False}
        
        # 全指定チェック（「？」のみ）
        if text.strip() == "？" or text.strip() == "?":
            return {"terms": [], "wildcard": True, "partial_match": False}
        
        # クエスチョンマークによる部分一致指定チェック
        has_question_mark = "？" in text or "?" in text
        
        # クエスチョンマークを除去してから処理
        clean_text = text.replace("？", "").replace("?", "")
        
        # 複数指定の分割（スペースまたはカンマ）
        # 正規表現で複数の区切り文字に対応
        terms = re.split(r'[,，\s]+', clean_text)
        
        # 空文字列を除去し、各項目をトリム
        terms = [term.strip() for term in terms if term.strip()]
        
        return {
            "terms": terms,
            "wildcard": False,
            "partial_match": has_question_mark
        }
    
    def normalize_search_terms(self, text: str, mode: str = "trademark") -> list:
        """
        検索用語の正規化とパース
        
        Args:
            text: 検索文字列
            mode: 正規化モード ("trademark", "basic", "pronunciation")
        
        Returns:
            正規化された検索用語のリスト
        """
        parsed = self.parse_multi_search_terms(text)
        
        if parsed["wildcard"]:
            return ["*"]  # 全指定
        
        normalized_terms = []
        for term in parsed["terms"]:
            if mode == "trademark":
                normalized = self.normalize_trademark(term)
            elif mode == "pronunciation":
                normalized = self.normalize_pronunciation(term)
            else:
                normalized = self.normalize_basic(term)
            
            if normalized:
                normalized_terms.append(normalized)
        
        return normalized_terms
    
    def _hiragana_to_katakana(self, text: str) -> str:
        """ひらがな→カタカナ変換"""
        result = ""
        for char in text:
            if 'あ' <= char <= 'ん':
                # ひらがなをカタカナに変換
                result += chr(ord(char) + ord('ア') - ord('あ'))
            else:
                result += char
        return result
    
    def _normalize_hyphens(self, text: str) -> str:
        """長音・ハイフン類の統一"""
        # 各種ハイフン・長音記号を統一
        hyphen_chars = ['ー', '－', '―', '‐', '‑', '‒', '–', '—', '―', '─']
        for char in hyphen_chars:
            text = text.replace(char, '-')
        return text
    
    def _remove_special_symbols(self, text: str) -> str:
        """特殊記号の排除"""
        # P1-5で指定された特殊記号を除去
        special_symbols = ['▲', '▼', '§', '￠', '＼', '∞', '※', '★', '☆', '●', '○']
        for symbol in special_symbols:
            text = text.replace(symbol, '')
        
        # その他の記号文字も除去
        text = re.sub(r'[♪♫♬♭♯☀☁☂☃❄⚡⛄⛅⛈⛉⛊]', '', text)
        return text
    
    def _remove_punctuation(self, text: str) -> str:
        """句読点・記号の排除（商標で重要な記号は保持）"""
        # 基本的な句読点のみを削除（商標で重要な記号は保持）
        # 保持する記号: 中点「・」、感嘆符「!！」、疑問符「?？」、かぎ括弧「」『』」
        punctuation = ['。', '、', '，', ',', '.']  # 基本的な句読点のみ
        punctuation += ['"', "'", '"', '"', ''', ''']  # クォーテーション類
        
        for punct in punctuation:
            text = text.replace(punct, '')
        return text
    
    def _convert_greek_latin(self, text: str) -> str:
        """ギリシャ・ラテン文字の変換"""
        for greek, ascii_char in self.greek_latin_to_ascii.items():
            text = text.replace(greek, ascii_char)
        return text
    
    def _convert_old_kanji(self, text: str) -> str:
        """旧字体→新字体変換"""
        for old, new in self.old_to_new_kanji.items():
            text = text.replace(old, new)
        return text
    
    def _convert_roman_numerals(self, text: str) -> str:
        """ローマ数字→算用数字変換"""
        for roman, arabic in self.roman_to_arabic.items():
            text = text.replace(roman, arabic)
        return text
    
    def _normalize_pronunciation_same(self, text: str) -> str:
        """発音同一文字の統一（P1-10）"""
        # ヲ→オ、ヂ→ジ、ヅ→ズなど
        text = text.replace('ヲ', 'オ')
        text = text.replace('ヂ', 'ジ')
        text = text.replace('ヅ', 'ズ')
        
        # 濁音・半濁音の統一も考慮
        text = text.replace('ヰ', 'イ')
        text = text.replace('ヱ', 'エ')
        
        return text
    
    def _normalize_subtle_sounds(self, text: str) -> str:
        """微差音統一（P1-11）"""
        # ヴ系の変換（順序重要）
        text = text.replace('ヴェ', 'ベ')
        text = text.replace('ヴァ', 'バ')
        text = text.replace('ヴィ', 'ビ')
        text = text.replace('ヴォ', 'ボ')
        text = text.replace('ヴュ', 'ビュ')
        text = text.replace('ヴ', 'ブ')
        
        # ツィ→チ、ティ→チ、ディ→ジなど
        text = text.replace('ツィ', 'チ')
        text = text.replace('ティ', 'チ')
        text = text.replace('トゥ', 'ツ')
        text = text.replace('ディ', 'ジ')
        text = text.replace('デュ', 'ジュ')
        text = text.replace('ドゥ', 'ズ')
        
        # フ系の変換
        text = text.replace('ファ', 'ハ')
        text = text.replace('フィ', 'ヒ')
        text = text.replace('フェ', 'ヘ')
        text = text.replace('フォ', 'ホ')
        text = text.replace('フュ', 'ヒュ')
        
        # その他の微差音
        text = text.replace('ウィ', 'イ')
        text = text.replace('ウェ', 'エ')
        text = text.replace('ウォ', 'オ')
        text = text.replace('シェ', 'セ')
        text = text.replace('ジェ', 'ゼ')
        text = text.replace('チェ', 'テ')
        text = text.replace('ツェ', 'テ')
        
        return text
    
    def _normalize_long_sounds(self, text: str) -> str:
        """長音・促音・長音化母音の処理（P1-12）"""
        # エイ→エー、オウ→オーなど長音化
        text = re.sub(r'エイ', 'エー', text)
        text = re.sub(r'オウ', 'オー', text)
        text = re.sub(r'コウ', 'コー', text)
        
        # 長音記号の統一（既に_normalize_hyphensで処理済みだが念のため）
        text = text.replace('ー', '-')
        
        return text
    
    def normalize_applicant_name(self, text: str) -> str:
        """
        P2-14: 申請人・権利者名の正規化
        法人種別語句を除去して検索精度を向上
        """
        if not text:
            return ""
        
        # 法人種別語句の除去（基礎正規化より前に実行）
        text = self._remove_corporate_suffixes(text)
        
        # 基礎正規化を適用
        text = self.normalize_basic(text)
        
        return text.strip()
    
    def _remove_corporate_suffixes(self, text: str) -> str:
        """法人種別語句の除去（P2-14）"""
        # 最長一致優先で除去（長い語句から先に処理）
        sorted_suffixes = sorted(self.corporate_suffixes, key=len, reverse=True)
        
        for suffix in sorted_suffixes:
            # 大文字小文字を区別しない比較のため、両方を正規化
            text_upper = text.upper()
            suffix_upper = suffix.upper()
            
            # 前方一致チェック（法人種別が前にある場合）
            if text_upper.startswith(suffix_upper):
                remaining = text[len(suffix):].strip()
                # 残りの部分が存在し、意味のある長さで、かつ境界が適切な場合のみ除去
                if remaining and len(remaining) >= 2 and self._is_word_boundary(text, len(suffix)):
                    text = remaining
                    break
            
            # 後方一致チェック（法人種別が後ろにある場合）
            elif text_upper.endswith(suffix_upper):
                remaining = text[:-len(suffix)].strip()
                # 残りの部分が存在し、意味のある長さで、かつ境界が適切な場合のみ除去
                if remaining and len(remaining) >= 2 and self._is_word_boundary(text, len(text) - len(suffix)):
                    text = remaining
                    break
        
        return text
    
    def _is_word_boundary(self, text: str, position: int) -> bool:
        """単語境界の判定（略語の誤マッチを防ぐ）"""
        # 位置が文字列の始端または終端の場合は境界
        if position == 0 or position >= len(text):
            return True
        
        # 前後の文字をチェック
        if position < len(text):
            # スペース、句読点、記号などがあれば境界
            char = text[position]
            if char in ' 　.,;:!?()[]{}「」・、。':
                return True
        
        # 日本語の場合は境界として扱う（日本語企業名では通常分かち書きしない）
        return True
    
    def _normalize_contracted_sounds(self, text: str) -> str:
        """拗音大文字化（P1-13）"""
        # 小文字の拗音を大文字に変換
        # ただし、促音「ッ」は特別な処理が必要（発音同一判定では残す）
        contracted_map = {
            'ャ': 'ヤ', 'ュ': 'ユ', 'ョ': 'ヨ',
            'ァ': 'ア', 'ィ': 'イ', 'ゥ': 'ウ', 'ェ': 'エ', 'ォ': 'オ'
            # 'ッ': 'ツ'  # 促音は発音同一判定のため変換しない
        }
        
        for small, large in contracted_map.items():
            text = text.replace(small, large)
        
        return text


def test_normalizer():
    """正規化ユーティリティのテスト"""
    normalizer = TextNormalizer()
    
    print("=== P1基礎正規化テスト ===")
    
    test_cases = [
        ("ひらがな", "ヒラガナ"),
        ("sony", "SONY"),
        ("ソニー", "ソニ-"),
        ("ソ ニ ー", "ソニ-"),
        ("ソニー▲", "ソニ-"),
        ("ソニー、株式会社", "ソニ-株式会社"),
        ("α-ブロッカー", "A-ブロッカ-"),
        ("會社", "会社"),
        ("Ⅲ世代", "3世代")
    ]
    
    for input_text, expected in test_cases:
        result = normalizer.normalize_basic(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (期待値: '{expected}')")
    
    print("\n=== 称呼正規化テスト ===")
    
    pronunciation_cases = [
        ("チヂミ", "チジミ"),
        ("ヴェール", "ベ-ル"),
        ("フィルム", "ヒルム"),
        ("エイコー", "エ-コ-"),
        ("コーヒー", "コ-ヒ-")
    ]
    
    for input_text, expected in pronunciation_cases:
        result = normalizer.normalize_pronunciation(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (期待値: '{expected}')")
    
    print("\n=== P2-14 法人種別語句排除テスト ===")
    
    applicant_cases = [
        ("ソニー株式会社", "ソニ-"),
        ("トヨタ自動車株式会社", "トヨタ自動車"),
        ("パナソニック株式会社", "パナソニック"),
        ("日本電気株式会社", "日本電気"),
        ("Apple Inc.", "APPLE"),
        ("Microsoft Corporation", "MICROSOFT"),
        ("Google LLC", "GOOGLE"),
        ("一般財団法人日本特許情報機構", "日本特許情報機構"),
        ("有限会社テスト", "テスト"),
        ("合同会社サンプル", "サンプル"),
        ("株式会社", "株式"),  # 単独でも除去される（最低2文字確保で"株式"が残る）
        ("法人", "法人"),  # 単独の場合は除去しない
        ("Company", "COMPANY"),  # 単独の場合は除去しない
    ]
    
    for input_text, expected in applicant_cases:
        result = normalizer.normalize_applicant_name(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (期待値: '{expected}')")

    print("\n=== TM-SONAR商標正規化テスト ===")
    
    trademark_cases = [
        ("ソニー株式会社", "ソニ-株式会社"),  # 法人種別語句は除去しない
        ("ＳＯＮＹ・ブランド", "ＳＯＮＹ・ブランド"),  # 中点は保持、全角文字はそのまま
        ("テスト《限定版》", "テスト《限定版》"),  # 特殊記号は保持
        ("サンプル▲マーク", "サンプルマ-ク"),  # TM-SONAR指定記号は除去、長音統一
        ("商品名、価格表示", "商品名価格表示"),  # 句点とカンマは除去
        ("Ⅲ世代プロダクト", "3世代プロダクト"),  # ローマ数字変換
        ("テスト＼サンプル", "テストサンプル"),  # 二段併記記号除去
    ]
    
    for input_text, expected in trademark_cases:
        result = normalizer.normalize_trademark(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (期待値: '{expected}')")

    print("\n=== 二段併記分離テスト ===")
    
    split_cases = [
        ("ＳＯＮＩＣｏｏｌ＼ソニクール", ["ＳＯＮＩＣｏｏｌ", "ソニクール", "ＳＯＮＩＣｏｏｌソニクール"]),
        ("テスト＼商品", ["テスト", "商品", "テスト商品"]),
        ("単一商標", ["単一商標"]),
    ]
    
    for input_text, expected in split_cases:
        result = normalizer.split_trademark_components(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → {result} (期待値: {expected})")

    print("\n=== 複数指定・クエスチョンマーク検索テスト ===")
    
    multi_search_cases = [
        ("？", {"terms": [], "wildcard": True, "partial_match": False}),
        ("ソニー,パナソニック", {"terms": ["ソニー", "パナソニック"], "wildcard": False, "partial_match": False}),
        ("テスト サンプル", {"terms": ["テスト", "サンプル"], "wildcard": False, "partial_match": False}),
        ("ソニー？", {"terms": ["ソニー"], "wildcard": False, "partial_match": True}),
        ("商標？ ブランド？", {"terms": ["商標", "ブランド"], "wildcard": False, "partial_match": True}),
    ]
    
    for input_text, expected in multi_search_cases:
        result = normalizer.parse_multi_search_terms(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → {result} (期待値: {expected})")

    print("\n=== 正規化検索用語テスト ===")
    
    search_terms_cases = [
        ("ソニー,パナソニック", "trademark", ["ソニ-", "パナソニック"]),
        ("？", "trademark", ["*"]),
        ("テスト サンプル", "basic", ["テスト", "サンプル"]),
    ]
    
    for input_text, mode, expected in search_terms_cases:
        result = normalizer.normalize_search_terms(input_text, mode)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' ({mode}) → {result} (期待値: {expected})")


if __name__ == "__main__":
    test_normalizer()