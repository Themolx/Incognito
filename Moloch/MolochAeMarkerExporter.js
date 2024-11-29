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

    // Default export path
    var DEFAULT_EXPORT_PATH = "Y:\\MOLOCH_02426\\assets\\assets2D\\Inserts_EP01\\InsertTimelineMarkers\\marker_data.json";

    // Create UI Dialog
    function createDialog() {
        var dialog = new Window("dialog", "Marker Export and Renaming Tool");
        dialog.orientation = "column";
        dialog.alignChildren = "fill";

        // Mode selection group
        var modeGroup = dialog.add("group");
        modeGroup.orientation = "row";
        modeGroup.alignChildren = "center";
        var enableRenaming = modeGroup.add("checkbox", undefined, "Enable Marker Renaming");
        enableRenaming.value = false; // Default to false

        // Shot settings panel - initially hidden
        var shotSettingsPanel = dialog.add("panel", undefined, "Shot Naming Settings");
        shotSettingsPanel.orientation = "column";
        shotSettingsPanel.alignChildren = "left";
        shotSettingsPanel.visible = false;  // Hidden by default

        // Shot number group
        var shotGroup = shotSettingsPanel.add("group");
        shotGroup.add("statictext", undefined, "Starting Shot Number:");
        var shotInput = shotGroup.add("edittext", undefined, "580");
        shotInput.characters = 10;

        // Increment group
        var incrementGroup = shotSettingsPanel.add("group");
        incrementGroup.add("statictext", undefined, "Increment By:");
        var incrementInput = incrementGroup.add("edittext", undefined, "20");
        incrementInput.characters = 10;

        // Special shots group
        var specialShotsGroup = shotSettingsPanel.add("group");
        specialShotsGroup.orientation = "column";
        specialShotsGroup.alignChildren = "left";
        specialShotsGroup.add("statictext", undefined, "Special Shots (comma-separated):");
        var specialShotsInput = specialShotsGroup.add("edittext", [0, 0, 300, 60], "", {multiline: true});
        var specialShotsHelp = specialShotsGroup.add("statictext", undefined, "Example: 545, 567, 573");
        specialShotsHelp.graphics.foregroundColor = specialShotsHelp.graphics.newPen(specialShotsHelp.graphics.PenType.SOLID_COLOR, [0.5, 0.5, 0.5], 1);

        // Export path group
        var exportGroup = dialog.add("group");
        exportGroup.orientation = "row";
        exportGroup.alignChildren = "center";
        exportGroup.add("statictext", undefined, "Export Path:");
        var exportPath = exportGroup.add("edittext", undefined, DEFAULT_EXPORT_PATH);
        exportPath.characters = 50;
        var browseButton = exportGroup.add("button", undefined, "Browse...");

        // Buttons
        var buttonGroup = dialog.add("group");
        var exportButton = buttonGroup.add("button", undefined, "Export");
        var cancelButton = buttonGroup.add("button", undefined, "Cancel");

        // Enable/Disable renaming checkbox functionality
        enableRenaming.onClick = function() {
            shotSettingsPanel.visible = enableRenaming.value;
            dialog.layout.layout(true);
        };

        // Browse button functionality
        browseButton.onClick = function() {
            var file = File.saveDialog("Save JSON file", "JSON files:*.json");
            if (file) {
                exportPath.text = file.fsName;
            }
        };

        return {
            dialog: dialog,
            enableRenaming: enableRenaming,
            shotInput: shotInput,
            incrementInput: incrementInput,
            specialShotsInput: specialShotsInput,
            exportPath: exportPath,
            exportButton: exportButton,
            cancelButton: cancelButton
        };
    }

    // Other helper functions remain the same
    function parseSpecialShots(specialShotsText) {
        if (!specialShotsText || !specialShotsText.trim()) return [];
        
        try {
            var shots = specialShotsText.split(",")
                .map(function(shot) {
                    var cleanShot = shot.replace(/[^\d\s]/g, '').trim();
                    var num = parseInt(cleanShot);
                    if (isNaN(num)) {
                        throw new Error("Invalid shot number: " + shot);
                    }
                    return num;
                })
                .filter(function(shot) {
                    return !isNaN(shot) && shot > 0;
                });
            
            return shots.length === 0 ? [] : shots;
        } catch (error) {
            alert("Error parsing special shots: " + error.message + "\nPlease enter valid numbers separated by commas.");
            return [];
        }
    }

    function generateShotSequence(startShot, increment, specialShots, totalMarkers) {
        var sequence = [];
        var currentShot = startShot;
        var specialIndex = 0;
        var regularIndex = 0;

        while (sequence.length < totalMarkers) {
            if (specialIndex < specialShots.length) {
                var nextSpecial = specialShots[specialIndex];
                var nextRegular = currentShot + (regularIndex * increment);

                if (nextSpecial < nextRegular) {
                    sequence.push(nextSpecial);
                    specialIndex++;
                } else {
                    sequence.push(nextRegular);
                    regularIndex++;
                }
            } else {
                sequence.push(currentShot + (regularIndex * increment));
                regularIndex++;
            }
        }

        return sequence.slice(0, totalMarkers);
    }

    function writeJSONFile(data, filePath) {
        try {
            var folder = new Folder(filePath.substring(0, filePath.lastIndexOf("\\")));
            if (!folder.exists) {
                folder.create();
            }

            var file = new File(filePath);
            if (!file.name.match(/\.json$/i)) {
                file = new File(filePath + ".json");
            }
            
            if (file.open("w")) {
                var jsonString = JSON.stringify(data, null, 2);
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

    function padZero(num) {
        return num < 10 ? "0" + num : num.toString();
    }

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

    function preserveLeadingZeros(num) {
        var str = num.toString();
        while (str.length < 3) {
            str = '0' + str;
        }
        return str;
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
                frame: Math.round(markerTime * comp.frameRate) + 1001
            });
        }

        if (markers.length === 0) {
            alert("No markers found in composition!");
            return;
        }

        // Create and show dialog
        var ui = createDialog();
        
        ui.exportButton.onClick = function() {
            app.beginUndoGroup("Process Markers");

            try {
                var exportData = {
                    compositionName: comp.name,
                    frameRate: comp.frameRate,
                    frameStart: 1001,
                    markers: []
                };

                if (ui.enableRenaming.value) {
                    // Renaming mode
                    var startingShot = Number(ui.shotInput.text);
                    var increment = parseInt(ui.incrementInput.text) || 0;
                    var specialShots = parseSpecialShots(ui.specialShotsInput.text);

                    if (isNaN(startingShot) || isNaN(increment)) {
                        alert("Please enter valid numbers!");
                        return;
                    }

                    var shotSequence = generateShotSequence(startingShot, increment, specialShots, markers.length);

                    for (var i = 0; i < markers.length; i++) {
                        var marker = comp.markerProperty.keyValue(i + 1);
                        var currentShot = preserveLeadingZeros(shotSequence[i]);
                        var markerFrame = markers[i].frame;
                        
                        // Update marker in composition
                        marker.comment = "Shot_" + currentShot + " (Frame: " + markerFrame + ")";
                        comp.markerProperty.setValueAtKey(i + 1, marker);

                        exportData.markers.push({
                            shotNumber: currentShot,
                            frame: markerFrame,
                            seconds: markers[i].time,
                            timecode: timeToTimecode(markers[i].time, comp.frameRate),
                            name: "Shot_" + currentShot
                        });
                    }
                } else {
                    // Export-only mode (no renaming)
                    for (var i = 0; i < markers.length; i++) {
                        var marker = comp.markerProperty.keyValue(i + 1);
                        var markerFrame = markers[i].frame;
                        
                        exportData.markers.push({
                            originalName: marker.comment || ("Marker_" + (i + 1)),
                            frame: markerFrame,
                            seconds: markers[i].time,
                            timecode: timeToTimecode(markers[i].time, comp.frameRate)
                        });
                    }
                }

                if (writeJSONFile(exportData, ui.exportPath.text)) {
                    alert("Markers " + (ui.enableRenaming.value ? "renamed and " : "") + 
                          "exported successfully to:\n" + ui.exportPath.text);
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
