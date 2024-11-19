{
    // After Effects Script to Import Nuke Transform Data to Null Object
    // Save this as "ImportNukeTransformToNull.jsx"
    
    function getFirstKey(obj) {
        if (obj && typeof obj === 'object') {
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    return key;
                }
            }
        }
        return null;
    }
    
    function toFloat(value) {
        // Convert any value to a valid float
        var num = parseFloat(value);
        return isNaN(num) ? 0 : num;
    }
    
    function ensureValidPosition(pos) {
        // Ensure position is always a valid array with exactly 2 float values
        if (!Array.isArray(pos)) {
            return [0, 0];
        }
        return [toFloat(pos[0]), toFloat(pos[1])];
    }
    
    function importNukeTransformToNull() {
        app.beginUndoGroup("Import Nuke Transform to Null");
        
        try {
            // Make sure we have an active composition
            if (!app.project || !app.project.activeItem || !(app.project.activeItem instanceof CompItem)) {
                alert("Please select a composition first.");
                return;
            }
            
            var comp = app.project.activeItem;
            
            // Show file picker dialog
            var jsonFile = File.openDialog("Select Nuke transform data file", "JSON files:*.json");
            if (!jsonFile) return;
            
            // Read JSON file
            jsonFile.open('r');
            var jsonContent = jsonFile.read();
            jsonFile.close();
            
            // Parse JSON
            var transformData = JSON.parse(jsonContent);
            
            // Create a new null object
            var nullLayer = comp.layers.addNull();
            nullLayer.name = "Nuke Transform Data";
            
            // Get the first node's data
            var firstNodeKey = getFirstKey(transformData.nodes);
            var nodeData = transformData.nodes[firstNodeKey];
            
            // Get comp dimensions
            var compWidth = toFloat(comp.width);
            var compHeight = toFloat(comp.height);
            
            try {
                // Process position (translate) data
                if (nodeData.translate) {
                    // Remove existing keyframes
                    while (nullLayer.transform.position.numKeys > 0) {
                        nullLayer.transform.position.removeKey(1);
                    }
                    
                    if (Array.isArray(nodeData.translate) && nodeData.translate[0] && 'frame' in nodeData.translate[0]) {
                        // Animated position
                        for (var i = 0; i < nodeData.translate.length; i++) {
                            var frameData = nodeData.translate[i];
                            if (frameData && Array.isArray(frameData.value)) {
                                var pos = ensureValidPosition(frameData.value);
                                var aeX = toFloat(pos[0] + compWidth/2);
                                var aeY = toFloat(compHeight/2 - pos[1]);
                                var time = toFloat(frameData.frame)/comp.frameRate;
                                
                                try {
                                    nullLayer.transform.position.setValueAtTime(time, [aeX, aeY]);
                                } catch (e) {
                                    $.writeln("Frame " + frameData.frame + " error: " + e.toString());
                                    $.writeln("Values: " + aeX + ", " + aeY);
                                }
                            }
                        }
                    } else {
                        // Static position
                        var pos = ensureValidPosition(nodeData.translate);
                        var aeX = toFloat(pos[0] + compWidth/2);
                        var aeY = toFloat(compHeight/2 - pos[1]);
                        nullLayer.transform.position.setValue([aeX, aeY]);
                    }
                }
                
                // Set rotation (convert to float)
                if ('rotate' in nodeData) {
                    var rotationValue = toFloat(nodeData.rotate);
                    nullLayer.transform.rotation.setValue(rotationValue);
                }
                
                // Set scale (convert to float and percentage)
                if (nodeData.scale) {
                    var scale = ensureValidPosition(nodeData.scale);
                    nullLayer.transform.scale.setValue([
                        toFloat(scale[0] * 100),
                        toFloat(scale[1] * 100)
                    ]);
                }
                
                // Set anchor point (center)
                if (nodeData.center) {
                    var center = ensureValidPosition(nodeData.center);
                    nullLayer.transform.anchorPoint.setValue([
                        toFloat(center[0]),
                        toFloat(center[1])
                    ]);
                }
                
            } catch (error) {
                alert("Error setting transform values: " + error.toString());
                return;
            }
            
            // Select the null object
            nullLayer.selected = true;
            
            alert("Transform data imported successfully!");
            
        } catch (error) {
            alert("Error importing transform data: " + error.toString());
        }
        
        app.endUndoGroup();
    }
    
    // Create UI
    function createUI(thisObj) {
        var window = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Nuke Transform to Null", undefined, {resizeable: true});
        var content = window.add("group", undefined, "Controls");
        content.orientation = "column";
        
        var importButton = content.add("button", undefined, "Create Null with Nuke Transform");
        importButton.onClick = importNukeTransformToNull;
        
        window.layout.layout(true);
        window.layout.resize();
        window.center();
        
        return window;
    }
    
    // Show the panel
    var panel = createUI(this);
    if (panel instanceof Window) {
        panel.show();
    }
}
