import os
import json
from database import supabase

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def migrate_table(json_filename, table_name, mapping_func=None):
    file_path = os.path.join(DATA_DIR, json_filename)
    if not os.path.exists(file_path):
        print(f"Skipping {table_name}: {json_filename} not found.")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Special case for org_structure (usually a dict)
            if table_name == 'org_structure' and isinstance(data, dict):
                # Ensure it has components as JSONB
                record = {
                    'id': 'singleton',
                    'chart_image': data.get('chart_image', ''),
                    'pdf_url': data.get('pdf_url', ''),
                    'manual_url': data.get('manual_url', ''),
                    'components': data.get('components', [])
                }
                supabase.table('org_structure').upsert(record).execute()
                print("Successfully migrated org_structure.")
                return

            # Special case for carousel (usually a list of strings)
            if table_name == 'carousel' and isinstance(data, list):
                if data and isinstance(data[0], str):
                    records = [{'url': url, 'display_order': idx} for idx, url in enumerate(data)]
                    supabase.table('carousel').insert(records).execute()
                    print(f"Successfully migrated {len(records)} carousel images.")
                    return

            # Handle nested dictionary for policies
            if isinstance(data, dict) and table_name == 'policies':
                flattened = []
                for category, entries in data.items():
                    for entry in entries:
                        entry['category'] = category
                        flattened.append(entry)
                data = flattened

            if not isinstance(data, list):
                if isinstance(data, dict):
                    data = [data]
                else:
                    print(f"Skipping {table_name}: JSON data is not a list/dict.")
                    return

            if mapping_func:
                data = [mapping_func(item) for item in data]

            if data:
                print(f"Migrating {len(data)} records to '{table_name}'...")
                chunk_size = 50
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]
                    supabase.table(table_name).insert(chunk).execute()
                print(f"Successfully migrated {table_name}.")
            else:
                print(f"No records found for {table_name}.")

    except Exception as e:
        print(f"Error migrating {table_name}: {e}")

# Mapping functions
def map_event(item):
    return {'id': item.get('id'), 'date': item.get('date'), 'title': item.get('title'), 'category': item.get('category'), 'description': item.get('desc')}

def map_project(item):
    return {'id': item.get('id'), 'year': int(item.get('year')) if item.get('year') else None, 'title': item.get('title'), 'category': item.get('category'), 'description': item.get('description'), 'status': item.get('status'), 'image': item.get('image')}

def map_policy(item):
    return {'id': item.get('id'), 'category': item.get('category', 'other'), 'year': int(item.get('year')) if item.get('year') else 2026, 'title': item.get('title', 'Untitled'), 'description': item.get('description', ''), 'date': item.get('date', ''), 'status': item.get('status', 'Active'), 'file': item.get('file', ''), 'url': item.get('url', ''), 'video_file': item.get('video_file', ''), 'video_url': item.get('video_url', '')}

def map_kp(item):
    return {'id': item.get('id'), 'title': item.get('title'), 'description': item.get('description'), 'type': item.get('type'), 'date': item.get('date'), 'image': item.get('image'), 'file': item.get('file'), 'url': item.get('url'), 'action_text': item.get('action_text')}

def map_brochure(item):
    return {'id': item.get('id'), 'title': item.get('title'), 'url': item.get('url'), 'file': item.get('file')}

def map_tracking(item):
    return {'id': item.get('id'), 'corner': item.get('corner'), 'date': item.get('date'), 'time_started': item.get('time_started'), 'time_completed': item.get('time_completed'), 'type': item.get('type'), 'description': item.get('description'), 'updates_posted': item.get('updates_posted'), 'technical_officer': item.get('technical_officer')}

def map_news(item):
    title = item.get('title')
    if not title and item.get('caption'):
        # Take the first line of the caption as the title
        title = item.get('caption').split('\n')[0]
    return {
        'id': item.get('id'),
        'title': title or 'Untitled News',
        'content': item.get('caption') or item.get('content', ''),
        'date': item.get('post_date') or item.get('date'),
        'author': item.get('author', 'Admin'),
        'image': item.get('photos')[0] if item.get('photos') else item.get('image'),
        'url': item.get('post_url') or item.get('url')
    }

def map_livelihood(item):
    return {'id': item.get('id'), 'title': item.get('title'), 'description': item.get('description'), 'type': item.get('type'), 'url': item.get('url'), 'file': item.get('file'), 'date': item.get('date')}

def map_committee(item):
    return {'id': item.get('id'), 'name': item.get('name'), 'position': item.get('position'), 'role': item.get('role'), 'image': item.get('image')}

if __name__ == "__main__":
    if not supabase:
        print("Error: Supabase client not initialized.")
    else:
        migrate_table('events.json', 'events', mapping_func=map_event)
        migrate_table('projects.json', 'projects', mapping_func=map_project)
        migrate_table('policies.json', 'policies', mapping_func=map_policy)
        migrate_table('knowledge_products.json', 'knowledge_products', mapping_func=map_kp)
        migrate_table('brochures.json', 'brochures', mapping_func=map_brochure)
        migrate_table('tracking_matrix.json', 'tracking_matrix', mapping_func=map_tracking)
        migrate_table('news.json', 'news', mapping_func=map_news)
        migrate_table('livelihood_feeds.json', 'livelihood_feeds', mapping_func=map_livelihood)
        migrate_table('committee.json', 'committee', mapping_func=map_committee)
        migrate_table('org_structure.json', 'org_structure')
        migrate_table('carousel.json', 'carousel')
        
        # Migration for site_config
        config_file = os.path.join(DATA_DIR, 'site_config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                supabase.table('site_config').upsert({'id': 'singleton', 'config': config_data}).execute()
                print("Successfully migrated site_config.")

        print("Migration complete!")
