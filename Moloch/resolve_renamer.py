#!/usr/bin/env python
import os
import sys
import re

# Shot name mapping dictionary
SHOT_MAPPING = {
    'ME1_0050': 'EP01_G_050',
    'ME1_0060': 'EP01_G_060',
    'ME1_0070': 'EP01_G_070',
    'ME1_0080': 'EP01_G_080',
    'ME1_0090': 'EP01_G_090',
    'ME1_0100': 'EP01_D_100',
    'ME1_0110': 'EP01_G_110',
    'ME1_0120': 'EP01_D_120',
    'ME1_0130': 'EP01_D_130',
    'ME1_0140': 'EP01_D_140',
    'ME1_0150': 'EP01_D_150',
    'ME1_0160': 'EP01_D_160',
    'ME1_0170': 'EP01_D_170',
    'ME1_0180': 'EP01_D_180',
    'ME1_0190': 'EP01_D_190',
    'ME1_0200': 'EP01_D_200',
    'ME1_0210': 'EP01_D_210',
    'ME1_0220': 'EP01_G_220',
    'ME1_0230': 'EP01_G_230',
    'ME1_0240': 'EP01_G_240',
    'ME1_0250': 'EP01_G_250',
    'ME1_0260': 'EP01_G_260',
    'ME1_0270': 'EP01_G_270',
    'ME1_0280': 'EP01_G_280',
    'ME1_0290': 'EP01_G_290',
    'ME1_0300': 'EP01_G_300',
    'ME1_0310': 'EP01_G_310',
    'ME1_0320': 'EP01_G_320',
    'ME1_0330': 'EP01_G_330',
    'ME1_0340': 'EP01_G_340',
    'ME1_0350': 'EP01_G_350',
    'ME1_0360': 'EP01_D_360',
    'ME1_0370': 'EP01_D_370',
    'ME1_0380': 'EP01_D_380',
    'ME1_0390': 'EP01_D_390',
    'ME1_0400': 'EP01_D_400',
    'ME1_0410': 'EP01_D_410',
    'ME1_0420': 'EP01_D_420',
    'ME1_0430': 'EP01_D_430',
    'ME1_0440': 'EP01_G_440',
    'ME1_0470': 'EP01_D_470',
    'ME1_0480': 'EP01_D_480',
    'ME1_0490': 'EP01_D_490',
    'ME1_0500': 'EP01_G_500',
    'ME1_0510': 'EP01_D_510',
    'ME1_0520': 'EP01_D_520',
    'ME1_0570': 'EP01_G_570',
    'ME1_0580': 'EP01_D_580',
    'ME1_0590': 'EP01_G_590',
    'ME1_0700': 'EP01_G_700',
    'ME1_0710': 'EP01_G_710',
    'ME1_0720': 'EP01_G_720',
    'ME1_0730': 'EP01_D_730',
    'ME1_0740': 'EP01_D_740',
    'ME1_0750': 'EP01_G_750',
    'ME1_0760': 'EP01_G_760',
    'ME1_0770': 'EP01_G_770',
    'ME1_0780': 'EP01_G_780',
    'ME1_0790': 'EP01_D_790',
    'ME1_0800': 'EP01_D_800',
    'ME1_0810': 'EP01_D_810',
    'ME1_0830': 'EP01_D_830',
    'ME1_0832': 'EP01_D_832',
    'ME1_0850': 'EP01_G_850',
    'ME1_0860': 'EP01_G_860',
    'ME1_0870': 'EP01_G_870',
    'ME1_0880': 'EP01_G_880',
    'ME1_0900': 'EP01_G_900',
    'ME1_0910': 'EP01_G_910',
    'ME1_0920': 'EP01_G_920',
    'ME1_0930': 'EP01_G_930',
    'ME1_0940': 'EP01_F_940',
    'ME1_0950': 'EP01_F_950',
    'ME1_0960': 'EP01_F_960',
    'ME1_0970': 'EP01_F_970',
    'ME1_0980': 'EP01_F_980',
    'ME1_0990': 'EP01_D_990',
    'ME1_1000': 'EP01_D_1000',
    'ME1_1010': 'EP01_D_1010',
    'ME1_1020': 'EP01_D_1020',
    'ME1_1030': 'EP01_D_1030',
    'ME1_1040': 'EP01_D_1040',
    'ME1_1050': 'EP01_G_1050',
    'ME1_1060': 'EP01_G_1060',
    'ME1_9990': 'EP01_G_9990'
}

# Initialize DaVinci Resolve
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

def get_product_name(shot_name):
    """Get the product name for a given shot name from the mapping dictionary."""
    return SHOT_MAPPING.get(shot_name)

def extract_shot_name(file_path):
    """Extract ME1_XXXX shot name from file path."""
    try:
        # Handle full file path or just filename
        filename = os.path.basename(file_path)
        
        # Look for ME1_XXXX pattern anywhere in the filename
        match = re.search(r'ME1_\d{4}', filename)
        if match:
            shot_name = match.group(0)
            print(f"Found shot name: {shot_name} in {filename}")
            return shot_name
            
        print(f"No ME1_XXXX pattern found in: {filename}")
        return None
    except Exception as e:
        print(f"Error extracting shot name: {e}")
        return None

def replace_clip_name(item):
    """Add a marker with the product name to the clip."""
    try:
        # Get the current clip name
        try:
            media_pool_item = item.GetMediaPoolItem()
            file_path = media_pool_item.GetClipProperty("File Path")
            clip_name = media_pool_item.GetClipProperty("Clip Name")
        except:
            try:
                file_path = item.GetProperty("File Path")
                clip_name = item.GetProperty("Clip Name")
            except:
                print("Failed to get clip properties")
                return False

        if not file_path or not clip_name:
            print("Could not get clip properties")
            return False

        # Extract shot name and get corresponding product name
        shot_name = extract_shot_name(file_path)
        if not shot_name:
            print(f"No shot name found in: {clip_name}")
            return False

        product_name = get_product_name(shot_name)
        if not product_name:
            print(f"No product name found for shot: {shot_name}")
            return False

        print(f"Adding marker for: {clip_name} -> {product_name}")

        try:
            # Get clip start frame and duration
            start_frame = item.GetStart()
            duration = item.GetDuration()
            
            # First try to update the Media Pool item name
            if media_pool_item:
                try:
                    media_pool_item.SetClipProperty("Clip Name", product_name)
                except:
                    pass

            # Add a marker with the product name
            item.AddMarker(0, 'Blue', product_name, '', 1)
            
            print(f"Successfully added marker: {product_name}")
            return True

        except Exception as e:
            print(f"Error adding marker: {e}")
            return False

    except Exception as e:
        print(f"Error processing clip: {e}")
        return False

def update_timeline():
    """Update all clips in the active timeline."""
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("No active timeline found")
        return
    
    processed = 0
    skipped = 0
    
    print("\n=== Starting Timeline Update ===")
    
    # Process both video and audio tracks
    for track_type in ["video", "audio"]:
        track_count = timeline.GetTrackCount(track_type)
        print(f"\nProcessing {track_type} tracks. Count: {track_count}")
        
        for track_index in range(1, track_count + 1):
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items:
                print(f"No items in {track_type} track {track_index}")
                continue
                
            print(f"Processing {len(items)} items in {track_type} track {track_index}")
            for item in items:
                if replace_clip_name(item):
                    processed += 1
                else:
                    skipped += 1
    
    print("\n=== Update Complete ===")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print("========================")
    
    return processed, skipped

if __name__ == "__main__":
    update_timeline()
