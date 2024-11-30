#!/usr/bin/env python
import os
import re

# Initialize DaVinci Resolve
resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()

def clean_clip_name(clip_name):
    """Remove frame range suffix from clip name."""
    # Remove the frame range pattern [XXXX-XXXX]
    cleaned_name = re.sub(r'\.\[\d+-\d+\].*$', '', clip_name)
    return cleaned_name

def update_clip_name(item):
    """Update the clip name by removing frame range suffix."""
    try:
        # Get current clip name
        try:
            media_pool_item = item.GetMediaPoolItem()
            clip_name = media_pool_item.GetClipProperty("Clip Name")
        except:
            try:
                clip_name = item.GetProperty("Clip Name")
            except:
                print("Failed to get clip name")
                return False

        if not clip_name:
            print("No clip name found")
            return False

        # Clean the name
        new_name = clean_clip_name(clip_name)
        
        if new_name == clip_name:
            print(f"No changes needed for: {clip_name}")
            return False

        print(f"Renaming: {clip_name} -> {new_name}")

        # Try to update the name
        try:
            # Try to update via media pool item first
            if media_pool_item:
                media_pool_item.SetClipProperty("Clip Name", new_name)
            
            # Add a marker with the clean name
            item.AddMarker(0, 'Green', new_name, '', 1)
            
            print(f"Successfully processed: {new_name}")
            return True
        except Exception as e:
            print(f"Error updating clip: {e}")
            return False

    except Exception as e:
        print(f"Error processing clip: {e}")
        return False

def process_timeline():
    """Process all clips in the timeline."""
    timeline = project.GetCurrentTimeline()
    if not timeline:
        print("No active timeline found")
        return
    
    processed = 0
    skipped = 0
    
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
                if update_clip_name(item):
                    processed += 1
                else:
                    skipped += 1
    
    return processed, skipped

def create_update_window():
    """Create and show the update status window."""
    import tkinter as tk
    
    window = tk.Tk()
    window.title("Clean Names")
    window.attributes('-topmost', True)
    
    # Start the update process
    processed, skipped = process_timeline()
    
    # Show results
    result_text = f"Update Complete\n\nProcessed: {processed}\nSkipped: {skipped}"
    label = tk.Label(window, text=result_text, font=("Helvetica", 12), pady=20, padx=20)
    label.pack()
    
    # Add close button
    close_button = tk.Button(window, text="Close", command=window.destroy)
    close_button.pack(pady=10)
    
    window.geometry("200x150")
    window.mainloop()

if __name__ == "__main__":
    create_update_window()
