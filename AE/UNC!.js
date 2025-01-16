/*
UNC (Unusual Notification Case) Folder Organization Script v1.1
This script:
1. Provides two UNC handling options:
   - Weekly UNC folder creation with pattern: YYMMDD_ww##_UNC
   - Non-regular UNC subfolder creation in daily folders
2. Auto-detects and increments week numbers
3. Maintains folder structure organization
4. Handles file suffixing with _UNC

Usage:
1. Select compositions to process
2. Run script
3. Choose UNC type (Weekly/Non-regular)
4. Follow prompts for folder naming if needed
*/

{
    app.beginUndoGroup("UNC Folder Setup and Organization");

    // User configurable variables
    var DEBUG_MODE = false;
    var UNC_SUFFIX = "_UNC";
    var WEEKLY_FORMAT = "_ww"; // Format for weekly number
    var DEFAULT_UNC_FOLDER = "UNC";
    var UNC_PRESET_PATH = "P:/2D_TESTY_0000/AE_SCRIPTS/Source/UNC.aom";

    function debugLog(message) {
        if (DEBUG_MODE) {
            alert("🔍 DEBUG: " + message);
        }
    }

    function getProjectFolderPath() {
        var projectPath = app.project.file.path;
        debugLog("RAW PATH: " + projectPath);
        
        var pathParts = projectPath.split(/[\\\/]/);
        var drive = pathParts[1].charAt(0).toUpperCase();
        var project = pathParts[2];
        
        return drive + ":\\" + project;
    }

    function findDailiesFolder(projectFolderPath) {
        var dailiesVariants = ["_dailies", "dailies", "_Dailies", "Dailies"];
        var searchPaths = [projectFolderPath, projectFolderPath + "\\output"];
        
        for (var pathIndex = 0; pathIndex < searchPaths.length; pathIndex++) {
            var basePath = searchPaths[pathIndex];
            
            for (var i = 0; i < dailiesVariants.length; i++) {
                var dailiesPath = basePath + "\\" + dailiesVariants[i];
                var currentFolder = new Folder(dailiesPath);
                
                if (currentFolder.exists) {
                    return currentFolder;
                }
            }
        }
        
        alert("ERROR: No dailies folder found!");
        return null;
    }

    function getTodayDateString() {
        var date = new Date();
        return date.getFullYear().toString().substr(-2) +
               padNumber(date.getMonth() + 1, 2) +
               padNumber(date.getDate(), 2);
    }

    function getNextWeekNumber(dailiesFolder) {
        var files = dailiesFolder.getFiles();
        var highestWeek = 0;
        
        // Updated pattern to match _ww##_UNC regardless of preceding numbers
        var weekPattern = new RegExp("_ww(\\d+)_UNC$", "i");
        
        for (var i = 0; i < files.length; i++) {
            var folderName = files[i].name;
            var match = folderName.match(weekPattern);
            if (match) {
                var weekNum = parseInt(match[1]);
                highestWeek = Math.max(highestWeek, weekNum);
            }
        }
        
        return highestWeek + 1;
    }

    function createTodayFolder(parentFolder) {
        var dateString = getTodayDateString();
        var todayFolder = new Folder(parentFolder.fsName + "\\" + dateString);
        
        if (!todayFolder.exists) {
            if (!todayFolder.create()) {
                alert("ERROR: Failed to create today's folder!");
                return null;
            }
        }
        
        return todayFolder;
    }

    function createWeeklyUNCFolder(dailiesFolder) {
        var dateString = getTodayDateString();
        var nextWeek = getNextWeekNumber(dailiesFolder);
        var folderName = dateString + WEEKLY_FORMAT + padNumber(nextWeek, 2) + UNC_SUFFIX;
        var weekFolder = new Folder(dailiesFolder.fsName + "\\" + folderName);
        
        if (!weekFolder.exists) {
            if (!weekFolder.create()) {
                alert("ERROR: Failed to create weekly UNC folder!");
                return null;
            }
        }
        
        return weekFolder;
    }

    function createNonRegularUNCFolder(todayFolder, customName) {
        var uncName = customName || DEFAULT_UNC_FOLDER;
        
        var uncFolder = new Folder(todayFolder.fsName + "\\" + uncName);
        
        if (!uncFolder.exists) {
            if (!uncFolder.create()) {
                alert("ERROR: Failed to create UNC folder!");
                return null;
            }
        }
        
        return uncFolder;
    }

    function padNumber(number, width) {
        var numString = number.toString();
        while (numString.length < width) {
            numString = "0" + numString;
        }
        return numString;
    }

    function hasUNCsuffix(str) {
        return str.substr(-UNC_SUFFIX.length) === UNC_SUFFIX;
    }

    function checkUNCPresetExists() {
        // Create a temporary comp to check templates
        var tempComp = app.project.items.addComp("TempComp", 1920, 1080, 1, 1, 30);
        var renderQueueItem = app.project.renderQueue.items.add(tempComp);
        var outputModule = renderQueueItem.outputModule(1);
        
        var templates = outputModule.templates;
        var exists = false;
        
        for (var i = 0; i < templates.length; i++) {
            if (templates[i].toLowerCase() === "unc") {
                exists = true;
                break;
            }
        }
        
        // Clean up
        renderQueueItem.remove();
        tempComp.remove();
        
        return exists;
    }

    function createUNCPreset() {
        try {
            debugLog("Creating new UNC preset");
            
            // Try to load from preset file first
            var presetFile = new File(UNC_PRESET_PATH);
            if (presetFile.exists) {
                debugLog("Found UNC preset file at: " + UNC_PRESET_PATH);
                
                // Create a temporary comp to apply the preset
                var tempComp = app.project.items.addComp("TempComp", 1920, 1080, 1, 1, 30);
                var renderQueueItem = app.project.renderQueue.items.add(tempComp);
                var outputModule = renderQueueItem.outputModule(1);
                
                try {
                    outputModule.loadSettings(presetFile.fsName);
                    outputModule.saveAsTemplate("UNC");
                    debugLog("Successfully loaded and saved UNC preset from file");
                    
                    // Clean up
                    renderQueueItem.remove();
                    tempComp.remove();
                    return true;
                } catch (loadError) {
                    debugLog("Error loading preset file: " + loadError.toString());
                }
            }
            
            debugLog("Creating UNC preset manually");
            
            // Create a temporary comp to apply the preset
            var tempComp = app.project.items.addComp("TempComp", 1920, 1080, 1, 1, 30);
            var renderQueueItem = app.project.renderQueue.items.add(tempComp);
            var outputModule = renderQueueItem.outputModule(1);

            // Set up UNC settings manually
            var uncSettings = {
                "Format": "QuickTime",
                "Video Codec": "Apple ProRes 4444 XQ",
                "Output Audio": false,
                "Channels": "RGB",
                "Depth": "Trillions of Colors+",
                "Color": true,
                "Quality": 100,
                "Fast Start": true,
                "Resize": false,
                "Crop": false,
                "Use Comp Frame Rate": true
            };

            // Apply settings
            for (var key in uncSettings) {
                try {
                    outputModule.setSetting(key, uncSettings[key]);
                } catch (settingError) {
                    debugLog("Error setting " + key + ": " + settingError.toString());
                }
            }

            // Save as template
            outputModule.saveAsTemplate("UNC");

            // Clean up
            renderQueueItem.remove();
            tempComp.remove();

            debugLog("UNC preset created successfully");
            return true;

        } catch (error) {
            alert("Error creating UNC preset:\n" + error.toString());
            return false;
        }
    }

    function configureOutputModule(outputModule) {
        try {
            // Check if UNC template exists, create if it doesn't
            if (!checkUNCPresetExists()) {
                if (!createUNCPreset()) {
                    throw new Error("Failed to create UNC preset");
                }
            }
            
            // Apply UNC template
            outputModule.applyTemplate("UNC");
            return outputModule;
            
        } catch (error) {
            alert("Error configuring output module: " + error.toString());
            return null;
        }
    }

    function setupRenderQueue(outputFolder, isWeeklyUNC) {
        var selectedItems = app.project.selection;
        var comps = [];
        
        for (var i = 0; i < selectedItems.length; i++) {
            if (selectedItems[i] instanceof CompItem) {
                comps.push(selectedItems[i]);
            }
        }
        
        for (var i = 0; i < comps.length; i++) {
            var renderQueueItem = app.project.renderQueue.items.add(comps[i]);
            var outputModule = renderQueueItem.outputModule(1);

            // Handle filename - always add _UNC suffix if not present
            var originalName = comps[i].name;
            var outputName = hasUNCsuffix(originalName) ? originalName : originalName + UNC_SUFFIX;
            
            var outputFile = new File(outputFolder.fsName + "\\" + outputName);
            outputModule.file = outputFile;

            // Configure output module with standard settings
            configureOutputModule(outputModule);
        }
    }

    function getTodayFolders(dailiesFolder) {
        var dateString = getTodayDateString();
        var todayFolder = new Folder(dailiesFolder.fsName + "\\" + dateString);
        var folders = [];
        
        if (todayFolder.exists) {
            var items = todayFolder.getFiles();
            for (var i = 0; i < items.length; i++) {
                if (items[i] instanceof Folder) {
                    folders.push(items[i].name);
                }
            }
        }
        
        return folders;
    }

    function showUNCDialog(dailiesFolder) {
        var dialog = new Window("dialog", "UNC Folder Setup");
        dialog.orientation = "column";
        dialog.alignChildren = ["center", "top"];
        dialog.spacing = 10;
        dialog.margins = 16;

        // Add logo or title
        var titleGroup = dialog.add("group");
        titleGroup.add("statictext", undefined, "UNC Folder Setup").graphics.font = ScriptUI.newFont("Arial", "BOLD", 16);

        // Add description
        var descGroup = dialog.add("group");
        descGroup.preferredSize.width = 300;
        var descText = descGroup.add("statictext", undefined, "Choose the type of UNC folder to create and set up render queue for selected compositions.", {multiline: true});
        descText.alignment = ["fill", "top"];

        // Radio buttons for UNC type
        var typePanel = dialog.add("panel", undefined, "UNC Type");
        typePanel.orientation = "column";
        typePanel.alignChildren = ["left", "top"];
        typePanel.margins = 15;
        var weeklyRadio = typePanel.add("radiobutton", undefined, "Weekly UNC (YYMMDD_ww##_UNC)");
        var nonRegularRadio = typePanel.add("radiobutton", undefined, "Non-regular UNC (Custom folder)");
        weeklyRadio.value = true;

        // Custom folder group
        var customGroup = dialog.add("group");
        customGroup.orientation = "column";
        customGroup.alignChildren = ["left", "top"];
        customGroup.margins = [0, 5, 0, 0];
        
        // Existing folders dropdown
        var dropdownGroup = customGroup.add("group");
        dropdownGroup.orientation = "column";
        dropdownGroup.alignChildren = ["left", "top"];
        var dropdownLabel = dropdownGroup.add("statictext", undefined, "Select existing folder (optional):");
        var folderDropdown = dropdownGroup.add("dropdownlist");
        folderDropdown.preferredSize.width = 200;
        
        // Get existing folders
        var existingFolders = getTodayFolders(dailiesFolder);
        folderDropdown.add("item", "-- Create New Folder --");
        for (var i = 0; i < existingFolders.length; i++) {
            folderDropdown.add("item", existingFolders[i]);
        }
        folderDropdown.selection = 0;

        // Custom folder name input
        var inputGroup = customGroup.add("group");
        inputGroup.orientation = "column";
        inputGroup.alignChildren = ["left", "top"];
        var customLabel = inputGroup.add("statictext", undefined, "New folder name:");
        var customInput = inputGroup.add("edittext", undefined, DEFAULT_UNC_FOLDER);
        customInput.preferredSize.width = 200;
        
        // Initially hide custom group
        customGroup.visible = false;

        // Show/hide custom input based on radio selection
        weeklyRadio.onClick = function() { 
            customGroup.visible = false; 
        };
        nonRegularRadio.onClick = function() { 
            customGroup.visible = true; 
        };

        // Handle dropdown selection
        folderDropdown.onChange = function() {
            if (folderDropdown.selection.index === 0) {
                // New folder selected
                inputGroup.visible = true;
                customInput.text = DEFAULT_UNC_FOLDER;
            } else {
                // Existing folder selected
                inputGroup.visible = false;
                customInput.text = folderDropdown.selection.text;
            }
        };

        // Buttons
        var buttonGroup = dialog.add("group");
        buttonGroup.alignment = ["center", "top"];
        var cancelBtn = buttonGroup.add("button", undefined, "Cancel");
        var okBtn = buttonGroup.add("button", undefined, "OK", {name: "ok"});

        // Status text
        var statusText = dialog.add("statictext", undefined, "");
        statusText.graphics.foregroundColor = statusText.graphics.newPen(statusText.graphics.PenType.SOLID_COLOR, [1, 0, 0, 1], 1);

        // Validate and handle results
        okBtn.onClick = function() {
            if (nonRegularRadio.value && (!customInput.text || customInput.text.toString().replace(/\s/g, '') === "")) {
                statusText.text = "Please enter a folder name.";
                return;
            }
            dialog.close(1);
        };

        cancelBtn.onClick = function() {
            dialog.close(0);
        };

        var result = dialog.show();
        
        if (result === 1) {
            return {
                isWeeklyUNC: weeklyRadio.value,
                customName: customInput.text ? customInput.text.toString() : DEFAULT_UNC_FOLDER,
                useExistingFolder: nonRegularRadio.value && folderDropdown.selection.index > 0
            };
        }
        return null;
    }

    function main() {
        debugLog("=== STARTING UNC SETUP ===");
        
        var projectFolderPath = getProjectFolderPath();
        if (!projectFolderPath) return;
        
        var dailiesFolder = findDailiesFolder(projectFolderPath);
        if (!dailiesFolder) return;
        
        // Show improved UI dialog
        var dialogResult = showUNCDialog(dailiesFolder);
        if (!dialogResult) return;
        
        var targetFolder;
        
        if (dialogResult.isWeeklyUNC) {
            // Weekly UNC
            targetFolder = createWeeklyUNCFolder(dailiesFolder);
        } else {
            // Non-regular UNC
            var todayFolder = createTodayFolder(dailiesFolder);
            if (!todayFolder) return;
            
            if (dialogResult.useExistingFolder) {
                // Use existing folder
                targetFolder = new Folder(todayFolder.fsName + "\\" + dialogResult.customName);
                if (!targetFolder.exists) {
                    alert("Error: Selected folder no longer exists!");
                    return;
                }
            } else {
                // Create new folder
                targetFolder = createNonRegularUNCFolder(todayFolder, dialogResult.customName);
            }
        }
        
        if (!targetFolder) return;
        
        setupRenderQueue(targetFolder, dialogResult.isWeeklyUNC);
        alert("UNC folder created and render queue set up successfully!");
    }

    main();
    
    app.endUndoGroup();
}