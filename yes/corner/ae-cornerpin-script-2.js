{
    // After Effects Script to Import Nuke CornerPin Data to Null Objects
    // Save this as "ImportNukeCornerPinToNulls.jsx"
    
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
            if (typeof pos === 'number') {
                return [toFloat(pos), toFloat(pos)];
            }
            return [0, 0];
        }
        // Ensure we have at least 2 values
        return [
            toFloat(pos[0] || 0),
            toFloat(pos[1] || 0)
        ];
    }
    
    function createCornerNull(comp, name, color) {
        var nullLayer = comp.layers.addNull();
        nullLayer.name = name;
        nullLayer.label = color;
        return nullLayer;
    }
    
    function setNullPosition(nullLayer, pos, comp, frameData, frameRate) {
        try {
            // Always ensure we have valid coordinates
            var position = ensureValidPosition(pos);
            var aeX = toFloat(position[0] + comp.width/2);
            var aeY = toFloat(comp.height/2 - position[1]);
            var posArray = [aeX, aeY];
            
            if (frameData && typeof frameData.frame !== 'undefined') {
                var time = toFloat(frameData.frame)/frameRate;
                nullLayer.transform.position.setValueAtTime(time, posArray);
            } else {
                nullLayer.transform.position.setValue(posArray);
            }
        } catch (e) {
            $.writeln("Position error for " + nullLayer.name + ": " + e.toString());
            $.writeln("Attempted values: " + JSON.stringify(position));
        }
    }
    
    function createCornerPinSolid(comp, cornerMap) {
        try {
            // Create a solid that matches the composition size
            var solid = comp.layers.addSolid([1, 1, 1], "CornerPin_Target", comp.width, comp.height, 1);
            solid.label = 2; // Cyan to match parent null
            
            // Add Corner Pin effect
            var cornerPinEffect = solid.property("ADBE Effect Parade").addProperty("ADBE Corner Pin");
            if (!cornerPinEffect) {
                throw new Error("Failed to add Corner Pin effect");
            }
            
            // Define the corner mapping (Nuke to AE corner order)
            var cornerMapping = {
                "to1": "Upper Left",
                "to2": "Upper Right",
                "to3": "Lower Right",
                "to4": "Lower Left"
            };
            
            // Link each corner to corresponding null
            for (var nukeCorner in cornerMapping) {
                if (!cornerMap[nukeCorner] || !cornerMap[nukeCorner].cornerNull) {
                    throw new Error("Missing null object for corner: " + nukeCorner);
                }
                
                var cornerPoint = cornerMapping[nukeCorner];
                var nullLayer = cornerMap[nukeCorner].cornerNull;
                
                // Get point property
                var pointProperty = cornerPinEffect.property(cornerPoint);
                if (!pointProperty) {
                    throw new Error("Failed to access point property " + cornerPoint);
                }
                
                // Set expression
                var expression = [
                    "L = thisComp.layer(\"" + nullLayer.name + "\");",
                    "L.toComp(L.anchorPoint);"
                ].join("\n");
                
                pointProperty.expression = expression;
            }
            
            // Move solid to bottom of the null stack
            solid.moveAfter(cornerMap.to4.cornerNull);
            
            return solid;
            
        } catch (e) {
            $.writeln("Error creating corner pin solid: " + e.toString());
            alert("Error creating corner pin solid: " + e.toString());
            return null;
        }
    }
    
    function importNukeCornerPinToNulls() {
        app.beginUndoGroup("Import Nuke CornerPin to Nulls");
        
        try {
            // Make sure we have an active composition
            if (!app.project || !app.project.activeItem || !(app.project.activeItem instanceof CompItem)) {
                alert("Please select a composition first.");
                return;
            }
            
            var comp = app.project.activeItem;
            
            // Show file picker dialog
            var jsonFile = File.openDialog("Select Nuke corner pin data file", "JSON files:*.json");
            if (!jsonFile) return;
            
            jsonFile.open('r');
            var jsonContent = jsonFile.read();
            jsonFile.close();
            
            var nodeData = JSON.parse(jsonContent);
            if (!nodeData || !nodeData.nodes) {
                throw new Error("Invalid JSON data structure");
            }
            
            // Get the first corner pin node's data
            var firstNodeKey = getFirstKey(nodeData.nodes);
            if (!firstNodeKey || !nodeData.nodes[firstNodeKey]) {
                throw new Error("No valid corner pin data found in the file.");
            }
            
            var cornerPinData = nodeData.nodes[firstNodeKey].data;
            if (!cornerPinData) {
                throw new Error("Invalid corner pin data structure.");
            }
            
            // Create parent null for organization
            var parentNull = comp.layers.addNull();
            parentNull.name = "CornerPin_Control (Red=TL, Green=TR, Purple=BR, Yellow=BL)";
            parentNull.label = 2; // Make it cyan for visibility
            
            // Create nulls for each corner with specific colors
            var cornerMap = {
                to1: {
                    cornerNull: createCornerNull(comp, "Corner_TL (Top Left)", 9), // Red
                    name: "Top Left"
                },
                to2: {
                    cornerNull: createCornerNull(comp, "Corner_TR (Top Right)", 13), // Green
                    name: "Top Right"
                },
                to3: {
                    cornerNull: createCornerNull(comp, "Corner_BR (Bottom Right)", 5), // Purple
                    name: "Bottom Right"
                },
                to4: {
                    cornerNull: createCornerNull(comp, "Corner_BL (Bottom Left)", 3), // Yellow
                    name: "Bottom Left"
                }
            };
            
            // Process each corner
            for (var corner in cornerMap) {
                if (cornerPinData[corner]) {
                    var cornerData = cornerPinData[corner];
                    var nullObj = cornerMap[corner].cornerNull;
                    
                    if (!nullObj) {
                        throw new Error("Failed to create null object for corner: " + corner);
                    }
                    
                    // Clear existing keyframes
                    while (nullObj.transform.position.numKeys > 0) {
                        nullObj.transform.position.removeKey(1);
                    }
                    
                    if (Array.isArray(cornerData) && cornerData[0] && 'frame' in cornerData[0]) {
                        // Animated position
                        for (var i = 0; i < cornerData.length; i++) {
                            var frameData = cornerData[i];
                            if (frameData && frameData.value) {
                                setNullPosition(nullObj, frameData.value, comp, frameData, comp.frameRate);
                            }
                        }
                    } else {
                        // Static position
                        setNullPosition(nullObj, cornerData, comp);
                    }
                    
                    // Parent to control null
                    nullObj.parent = parentNull;
                }
            }
            
            // Create the solid with corner pin effect
            var cornerPinSolid = createCornerPinSolid(comp, cornerMap);
            if (!cornerPinSolid) {
                throw new Error("Failed to create corner pin solid");
            }
            cornerPinSolid.parent = parentNull;
            
            // Select the parent null
            parentNull.selected = true;
            
            alert("Corner pin nulls and target solid created successfully!");
            
        } catch (error) {
            alert("Error importing corner pin data: " + error.toString() + 
                  "\nCheck the ExtendScript debugger for more details.");
            $.writeln("Detailed error: " + error.toString());
        }
        
        app.endUndoGroup();
    }
    
    // Create UI
    function createUI(thisObj) {
        var window = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Nuke CornerPin to Nulls", undefined, {resizeable: true});
        var content = window.add("group", undefined, "Controls");
        content.orientation = "column";
        
        var importButton = content.add("button", undefined, "Create Corner Pin Nulls");
        importButton.onClick = importNukeCornerPinToNulls;
        
        var helpText = content.add("statictext", undefined, 
            "Creates 4 corner nulls and a solid with Corner Pin effect:\nRed (TL), Green (TR),\nPurple (BR), Yellow (BL)");
        helpText.alignment = ["center", "top"];
        
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