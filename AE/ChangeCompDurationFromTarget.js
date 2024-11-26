// Match Composition Durations
// This script matches the duration of the second selected composition to the first one
{
    function matchCompDurations() {
        var project = app.project;
        
        // Check if project exists
        if (!project) {
            alert("Please open a project first.");
            return;
        }
        
        // Get selected compositions
        var selectedItems = project.selection;
        
        // Validate selection
        if (selectedItems.length !== 2) {
            alert("Please select exactly two compositions.\nFirst select the source composition (reference duration),\nthen select the target composition (to be adjusted).");
            return;
        }
        
        // Check if both selected items are compositions
        if (!(selectedItems[0] instanceof CompItem) || !(selectedItems[1] instanceof CompItem)) {
            alert("Both selected items must be compositions.");
            return;
        }
        
        // Store compositions for clarity
        var sourceComp = selectedItems[0];
        var targetComp = selectedItems[1];
        
        // Store original duration for undo
        var originalDuration = targetComp.duration;
        
        // Perform the duration match
        app.beginUndoGroup("Match Composition Durations");
        
        try {
            targetComp.duration = sourceComp.duration;
            alert("Success!\n\nTarget composition duration has been adjusted to match source composition.\n\nSource: " + sourceComp.name + " (" + timeToFrames(sourceComp.duration, sourceComp.frameRate) + " frames)\nTarget: " + targetComp.name + " (" + timeToFrames(targetComp.duration, targetComp.frameRate) + " frames)");
        } catch (error) {
            alert("An error occurred: " + error.toString());
            // Attempt to restore original duration
            targetComp.duration = originalDuration;
        }
        
        app.endUndoGroup();
    }
    
    // Helper function to convert time to frames
    function timeToFrames(time, fps) {
        return Math.round(time * fps);
    }
    
    // Run the script
    matchCompDurations();
}
