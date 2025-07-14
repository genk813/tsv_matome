import os
import sqlite3

def get_file_size_mb(file_path):
    """Get file size in MB"""
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    return 0

def count_files_in_directory(directory):
    """Count files in a directory"""
    if os.path.exists(directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        return len(files)
    return 0

def get_total_size_of_directory(directory):
    """Get total size of all files in a directory in MB"""
    total_size = 0
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
    return total_size / (1024 * 1024)

def get_database_stats(db_path):
    """Get basic database statistics"""
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Get row counts for main tables
        table_stats = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_stats[table_name] = count
        
        conn.close()
        return table_stats
    except Exception as e:
        return f"Error: {str(e)}"

# Main execution
if __name__ == "__main__":
    base_path = r"C:\Users\ygenk\Desktop\TMCloud"
    
    print("TMCloud Project Statistics")
    print("=" * 50)
    
    # 1. Database file size
    db_path = os.path.join(base_path, "output.db")
    db_size = get_file_size_mb(db_path)
    print(f"\n1. Database Size:")
    print(f"   output.db: {db_size:.2f} MB")
    
    # 2. Number of images
    images_path = os.path.join(base_path, "images", "final_complete")
    num_images = count_files_in_directory(images_path)
    print(f"\n2. Number of Images:")
    print(f"   images/final_complete/: {num_images} files")
    
    # 3. Total size of images
    total_image_size = get_total_size_of_directory(images_path)
    print(f"\n3. Total Size of Images:")
    print(f"   images/final_complete/: {total_image_size:.2f} MB")
    
    # 4. Average image size
    if num_images > 0:
        avg_size = total_image_size / num_images
        print(f"   Average image size: {avg_size:.3f} MB")
    
    # 5. Database statistics
    print(f"\n4. Database Table Statistics:")
    db_stats = get_database_stats(db_path)
    if isinstance(db_stats, dict):
        for table, count in sorted(db_stats.items()):
            print(f"   {table}: {count:,} rows")
    else:
        print(f"   {db_stats}")
    
    # 6. .gitignore status
    gitignore_path = os.path.join(base_path, ".gitignore")
    gitignore_exists = os.path.exists(gitignore_path)
    print(f"\n5. .gitignore Status:")
    print(f"   Exists: {'Yes' if gitignore_exists else 'No'}")
    if gitignore_exists:
        print(f"   Size: {os.path.getsize(gitignore_path)} bytes")
        print(f"   Key entries: database files, images/, tsv_data/, logs, Python cache, etc.")