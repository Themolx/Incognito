{
    // Get the active composition
    function getActiveComp() {
        var comp = app.project.activeItem;
        if (!comp || !(comp instanceof CompItem)) {
            alert("Please select a composition!");
            return null;
        }
        return comp;
    }

    // Create UI Dialog
    function createDialog() {
        var dialog = new Window("dialog", "Marker Renaming and Export");
        dialog.orientation = "column";
        dialog.alignChildren = "fill";

        // Shot number group
        var shotGroup = dialog.add("group");
        shotGroup.add("statictext", undefined, "Starting Shot Number:");
        var shotInput = shotGroup.add("edittext", undefined, "580");
        shotInput.characters = 10;

        // Increment group
        var incrementGroup = dialog.add("group");
        incrementGroup.add("statictext", undefined, "Increment By:");
        var incrementInput = incrementGroup.add("edittext", undefined, "20");
        incrementInput.characters = 10;

        // Export path group
        var exportGroup = dialog.add("group");
        exportGroup.add("statictext", undefined, "Export Path:");
        var exportPath = exportGroup.add("edittext", undefined, "~/Desktop/marker_data.json");
        exportPath.characters = 30;
        var browseButton = exportGroup.add("button", undefined, "Browse...");

        // Buttons
        var buttonGroup = dialog.add("group");
        var okButton = buttonGroup.add("button", undefined, "OK");
        var cancelButton = buttonGroup.add("button", undefined, "Cancel");

        // Browse button functionality
        browseButton.onClick = function() {
            var file = File.saveDialog("Save JSON file", "JSON files:*.json");
            if (file) {
                exportPath.text = file.fsName;
            }
        };

        return {
            dialog: dialog,
            shotInput: shotInput,
            incrementInput: incrementInput,
            exportPath: exportPath,
            okButton: okButton,
            cancelButton: cancelButton
        };
    }

    // Function to safely write JSON file
    function writeJSONFile(data, filePath) {
        try {
            // Create file object
            var file = new File(filePath);
            
            // Make sure we have a .json extension
            if (!file.name.match(/\.json$/i)) {
                file = new File(filePath + ".json");
            }
            
            // Open file for writing
            if (file.open("w")) {
                // Convert data to string with pretty formatting
                var jsonString = JSON.stringify(data, null, 2);
                
                // Write and close
                file.encoding = "UTF-8";
                file.write(jsonString);
                file.close();
                
                return true;
            } else {
                alert("Could not open file for writing: " + file.error);
                return false;
            }
        } catch (error) {
            alert("Error writing file: " + error.toString());
            return false;
        }
    }

    // Helper function to pad numbers with leading zeros (replacement for padStart)
    function padZero(num) {
        return num < 10 ? "0" + num : num.toString();
    }

    // Helper function to convert time to timecode
    function timeToTimecode(time, fps) {
        var hours = Math.floor(time / 3600);
        var minutes = Math.floor((time % 3600) / 60);
        var seconds = Math.floor(time % 60);
        var frames = Math.floor((time * fps) % fps);
        
        return padZero(hours) + ":" + 
               padZero(minutes) + ":" + 
               padZero(seconds) + ":" + 
               padZero(frames);
    }

    // Main function
    function main() {
        var comp = getActiveComp();
        if (!comp) return;

        // Get markers
        var markers = [];
        for (var i = 1; i <= comp.markerProperty.numKeys; i++) {
            var markerTime = comp.markerProperty.keyTime(i);
            markers.push({
                time: markerTime,
                frame: Math.round(markerTime * comp.frameRate)
            });
        }

        if (markers.length === 0) {
            alert("No markers found in composition!");
            return;
        }

        // Create and show dialog
        var ui = createDialog();
        
        ui.okButton.onClick = function() {
            var startingShot = parseInt(ui.shotInput.text);
            var increment = parseInt(ui.incrementInput.text);

            if (isNaN(startingShot) || isNaN(increment)) {
                alert("Please enter valid numbers!");
                return;
            }

            // Start undoable action
            app.beginUndoGroup("Rename Markers");

            try {
                // Process markers and prepare export data
                var exportData = {
                    compositionName: comp.name,
                    frameRate: comp.frameRate,
                    markers: []
                };

                for (var i = 0; i < markers.length; i++) {
                    var marker = comp.markerProperty.keyValue(i + 1);
                    var shotNumber = startingShot + (i * increment);
                    var markerFrame = markers[i].frame;
                    
                    // Update marker in composition
                    marker.comment = "Shot_" + shotNumber + " (Frame: " + markerFrame + ")";
                    comp.markerProperty.setValueAtKey(i + 1, marker);

                    // Add to export data
                    exportData.markers.push({
                        shotNumber: shotNumber,
                        frame: markerFrame,
                        seconds: markers[i].time,
                        timecode: timeToTimecode(markers[i].time, comp.frameRate),
                        name: "Shot_" + shotNumber
                    });
                }

                // Write JSON file
                if (writeJSONFile(exportData, ui.exportPath.text)) {
                    alert("Markers renamed and exported successfully to:\n" + ui.exportPath.text);
                    ui.dialog.close();
                }

            } catch (error) {
                alert("Error processing markers: " + error.toString());
            }

            app.endUndoGroup();
        };

        ui.cancelButton.onClick = function() {
            ui.dialog.close();
        };

        ui.dialog.show();
    }

    main();
}
