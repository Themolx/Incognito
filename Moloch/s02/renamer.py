#!/usr/bin/env python
import os
import sys
import re




# Initialize DaVinci Resolve
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()



def extract_shot_name(file_path):
    """Extract shot name (like 'EP02_G_110') from file path."""
    try:
        # Handle pattern like: /shots/S01E02/sqB/EP02_G_110 renderCompositingMain v004 (exr)
        # Extract only the shot name (EP02_G_110)
        match = re.search(r'/shots/[^/]+/[^/]+/([^\s]+)\s+renderCompositingMain', file_path)
        if match:
            shot_name = match.group(1)
            print(f"Found shot name: {shot_name} in {file_path}")
            return shot_name
        
        # Fallback: Try to extract just the shot name pattern (e.g., EP02_G_110)
        match = re.search(r'(EP\d+_[A-Z]_\d+)', file_path)
        if match:
            shot_name = match.group(1)
            print(f"Found shot name using fallback: {shot_name} in {file_path}")
            return shot_name
            
        print(f"No shot name pattern found in: {file_path}")
        return None
    except Exception as e:
        print(f"Error extracting shot name: {e}")
        return None

def replace_clip_name(item):
    """Update the clip name with the clean shot name (e.g., EP02_G_110)."""
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

        # Extract shot name directly from path
        shot_name = extract_shot_name(file_path)
        if not shot_name:
            print(f"No shot name found in: {clip_name}")
            return False

        print(f"Renaming clip: {clip_name} -> {shot_name}")

        try:
            # Update the Media Pool item name if possible
            if media_pool_item:
                try:
                    media_pool_item.SetClipProperty("Clip Name", shot_name)
                    print(f"Successfully renamed to: {shot_name}")
                    return True
                except Exception as e:
                    print(f"Error setting clip name: {e}")
                    return False
            else:
                print("Could not update clip name: No media pool item found")
                return False

        except Exception as e:
            print(f"Error renaming clip: {e}")
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
