{
    // Enable UI for script
    function buildUI(thisObj) {
        var mainWindow = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Render Queue Info", undefined, {resizeable: true});
        
        // Create UI elements
        var mainGroup = mainWindow.add("group");
        mainGroup.orientation = "column";
        
        var buttonGroup = mainGroup.add("group");
        buttonGroup.orientation = "row";
        
        var refreshButton = buttonGroup.add("button", undefined, "Refresh Queue Info");
        var saveButton = buttonGroup.add("button", undefined, "Save to File");
        
        var displayText = mainGroup.add("edittext", undefined, "", {multiline: true, scrollable: true});
        displayText.size = [400, 300];
        
        // Function to get render queue information
        function getRenderQueueInfo() {
            var rq = app.project.renderQueue;
            var info = "Render Queue Status:\n\n";
            
            if (rq.numItems == 0) {
                info += "Render Queue is empty\n";
                return info;
            }
            
            for (var i = 1; i <= rq.numItems; i++) {
                var item = rq.item(i);
                var comp = item.comp;
                
                info += "Item " + i + ":\n";
                info += "Composition: " + comp.name + "\n";
                info += "Duration: " + timeToString(comp.duration) + "\n";
                info += "Dimensions: " + comp.width + "x" + comp.height + "\n";
                info += "Frame Rate: " + comp.frameRate + " fps\n";
                info += "Status: " + item.status + "\n";
                
                // Get output module info
                if (item.outputModule(1)) {
                    var om = item.outputModule(1);
                    info += "Output Format: " + om.format + "\n";
                    info += "Output Path: " + om.file.fsName + "\n";
                }
                
                info += "\n";
            }
            
            return info;
        }
        
        // Helper function to convert time to string format
        function timeToString(time) {
            var seconds = Math.floor(time);
            var frames = Math.floor((time - seconds) * 30);
            var minutes = Math.floor(seconds / 60);
            seconds = seconds % 60;
            
            return minutes + ":" + 
                   (seconds < 10 ? "0" : "") + seconds + ":" + 
                   (frames < 10 ? "0" : "") + frames;
        }
        
        // Refresh button click handler
        refreshButton.onClick = function() {
            displayText.text = getRenderQueueInfo();
        }
        
        // Save button click handler
        saveButton.onClick = function() {
            var file = File.saveDialog("Save Render Queue Info", "Text Files:*.txt");
            if (file) {
                file.open("w");
                file.write(displayText.text);
                file.close();
                alert("Information saved successfully!");
            }
        }
        
        // Initial population of info
        displayText.text = getRenderQueueInfo();
        
        // Show the window if not docked
        if (mainWindow instanceof Window) {
            mainWindow.center();
            mainWindow.show();
        }
        
        return mainWindow;
    }
    
    // Create and show UI
    var scriptPanel = buildUI(this);
}
