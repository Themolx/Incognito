/*
Auto-versioning Render Queue Setup Script v1.6
This script:
1. Finds project folder path based on project token pattern
2. Locates dailies folder in project structure or output folder
3. Creates date-based folder for outputs
4. Auto-versions files if matching names exist
5. Sets up render queue with proper output paths

Usage:
1. Select compositions to render
2. Run script
3. Files will be auto-versioned if duplicates exist
*/

{
    app.beginUndoGroup("Process Project Path and Setup Render Queue");

    // User configurable variables
    var VERSION_PREFIX = "_v"; // Version number prefix
    var VERSION_PADDING = 2; // Number of digits for version number
    var DEFAULT_VERSION = 1; // Starting version number
    var DEBUG_MODE = false; // Enable detailed debugging

    function debugLog(message) {
        if (DEBUG_MODE) {
            alert("🔍 DEBUG: " + message);
        }
    }

    function getProjectFolderPath() {
        var projectPath = app.project.file.path;
        debugLog("RAW PATH: " + projectPath);
        
        var pathParts = projectPath.split(/[\\\/]/);
        for (var i = 0; i < pathParts.length; i++) {
            debugLog("Part " + i + ": [" + pathParts[i] + "]");
        }
        
        // Check if we have enough path segments
        if (pathParts.length < 3) {
            alert("ERROR: Path is too short to extract mapping and project token!");
            return null;
        }
        
        // Get drive letter and project token
        var drive = pathParts[1];
        var project = pathParts[2];
        
        debugLog("DRIVE BEFORE: [" + drive + "]");
        debugLog("PROJECT: [" + project + "]");

        // Force proper drive format
        drive = drive.charAt(0).toUpperCase();
        debugLog("DRIVE LETTER: [" + drive + "]");

        // Build the path correctly with backslashes
        var projectFolderPath = drive + ":\\" + project;
        debugLog("FINAL PATH: [" + projectFolderPath + "]");
        
        return projectFolderPath;
    }

    function findDailiesFolder(projectFolderPath) {
        debugLog("LOOKING FOR DAILIES IN: [" + projectFolderPath + "]");
        
        var dailiesVariants = ["_dailies", "dailies", "_Dailies", "Dailies"];
        var searchPaths = [
            projectFolderPath,                    // Check in project root
            projectFolderPath + "\\output"        // Check in output folder
        ];
        
        debugLog("Checking in paths: " + JSON.stringify(searchPaths));
        
        // Search in each base path
        for (var pathIndex = 0; pathIndex < searchPaths.length; pathIndex++) {
            var basePath = searchPaths[pathIndex];
            debugLog("Checking base path: [" + basePath + "]");
            
            // Try each dailies variant in this path
            for (var i = 0; i < dailiesVariants.length; i++) {
                var dailiesPath = basePath + "\\" + dailiesVariants[i];
                debugLog("TRYING: [" + dailiesPath + "]");
                
                var currentFolder = new Folder(dailiesPath);
                debugLog("EXISTS? " + currentFolder.exists);
                
                if (currentFolder.exists) {
                    debugLog("FOUND IT!: " + dailiesPath);
                    return currentFolder;
                }
            }
        }
        
        alert("ERROR: No dailies folder found in project or output folder!");
        return null;
    }

    function getTodayFolders(dailiesFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        padNumber(date.getMonth() + 1, 2) +
                        padNumber(date.getDate(), 2);
        var todayFolder = new Folder(dailiesFolder.fsName + "\\" + dateString);
        var folders = [];
        
        if (todayFolder.exists) {
            var items = todayFolder.getFiles();
            for (var i = 0; i < items.length; i++) {
                if (items[i] instanceof Folder) {
                    // Get folder stats safely
                    try {
                        var stats = items[i].getFiles();
                        folders.push({
                            name: items[i].name,
                            modified: items[i].modified ? new Date(items[i].modified).getTime() : 0,
                            path: items[i]
                        });
                    } catch(e) {
                        debugLog("Error getting folder stats: " + e);
                        // Still add the folder even if we can't get stats
                        folders.push({
                            name: items[i].name,
                            modified: 0,
                            path: items[i]
                        });
                    }
                }
            }
            
            // Sort folders by modification time, most recent first
            // Handle cases where modified time might be invalid
            folders.sort(function(a, b) {
                var timeA = a.modified || 0;
                var timeB = b.modified || 0;
                if (timeA === timeB) {
                    // If times are equal or invalid, sort by name
                    return a.name.localeCompare(b.name);
                }
                return timeB - timeA;
            });
        }
        
        return folders;
    }

    function showDailiesDialog(dailiesFolder) {
        var dialog = new Window("dialog", "Dailies Folder Setup");
        dialog.orientation = "column";
        dialog.alignChildren = ["center", "top"];
        dialog.spacing = 10;
        dialog.margins = 16;

        // Add title
        var titleGroup = dialog.add("group");
        titleGroup.add("statictext", undefined, "Dailies Folder Setup").graphics.font = ScriptUI.newFont("Arial", "BOLD", 16);

        // Add description
        var descGroup = dialog.add("group");
        descGroup.preferredSize.width = 300;
        var descText = descGroup.add("statictext", undefined, "Choose how to organize your dailies output.", {multiline: true});
        descText.alignment = ["fill", "top"];

        // Radio buttons for folder type
        var typePanel = dialog.add("panel", undefined, "Folder Type");
        typePanel.orientation = "column";
        typePanel.alignChildren = ["left", "top"];
        typePanel.margins = 15;
        var regularRadio = typePanel.add("radiobutton", undefined, "Regular (Date-based folder)");
        var nonRegularRadio = typePanel.add("radiobutton", undefined, "Custom (Subfolder in date folder)");
        regularRadio.value = true;

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
        
        // Get existing folders sorted by modification time
        var existingFolders = getTodayFolders(dailiesFolder);
        folderDropdown.add("item", "-- Create New Folder --");
        for (var i = 0; i < existingFolders.length; i++) {
            folderDropdown.add("item", existingFolders[i].name);
        }
        folderDropdown.selection = existingFolders.length > 0 ? 1 : 0; // Select most recent folder if available

        // Custom folder name input
        var inputGroup = customGroup.add("group");
        inputGroup.orientation = "column";
        inputGroup.alignChildren = ["left", "top"];
        var customLabel = inputGroup.add("statictext", undefined, "New folder name:");
        var customInput = inputGroup.add("edittext", undefined, "");
        customInput.preferredSize.width = 200;
        
        // Initially hide custom group
        customGroup.visible = false;

        // Show/hide custom input based on radio selection
        regularRadio.onClick = function() { 
            customGroup.visible = false; 
        };
        nonRegularRadio.onClick = function() { 
            customGroup.visible = true;
            if (existingFolders.length > 0) {
                folderDropdown.selection = 1; // Select most recent folder
                inputGroup.visible = false;
                customInput.text = existingFolders[0].name;
            }
        };

        // Handle dropdown selection
        folderDropdown.onChange = function() {
            if (folderDropdown.selection.index === 0) {
                // New folder selected
                inputGroup.visible = true;
                customInput.text = "";
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
                isRegular: regularRadio.value,
                customName: customInput.text ? customInput.text.toString() : "",
                useExistingFolder: nonRegularRadio.value && folderDropdown.selection.index > 0
            };
        }
        return null;
    }

    function createDateFolder(parentFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        padNumber(date.getMonth() + 1, 2) +
                        padNumber(date.getDate(), 2);
        
        var dateFolder = new Folder(parentFolder.fsName + "\\" + dateString);
        
        if (!dateFolder.exists) {
            if (!dateFolder.create()) {
                alert("ERROR: Failed to create date folder!");
                return null;
            }
        }
        
        return dateFolder;
    }

    function createCustomFolder(dateFolder, folderName) {
        var customFolder = new Folder(dateFolder.fsName + "\\" + folderName);
        
        if (!customFolder.exists) {
            if (!customFolder.create()) {
                alert("ERROR: Failed to create custom folder!");
                return null;
            }
        }
        
        return customFolder;
    }

    function getNextVersionNumber(folderPath, baseName) {
        var folder = new Folder(folderPath);
        var files = folder.getFiles();
        var highestVersion = 0;
        
        // Remove any existing version numbers from baseName
        baseName = baseName.replace(/_v\d+$/, '').replace(/v\d+$/, '');
        
        var versionRegexWithUnderscore = new RegExp(baseName.replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1") + 
                                    VERSION_PREFIX + "\\d{" + VERSION_PADDING + "}");
        var versionRegexNoUnderscore = new RegExp(baseName.replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1") + 
                                    "v\\d+");
        
        for (var i = 0; i < files.length; i++) {
            var fileName = files[i].name;
            if (fileName.match(versionRegexWithUnderscore)) {
                var version = parseInt(fileName.match(new RegExp(VERSION_PREFIX + "(\\d+)"))[1]);
                highestVersion = Math.max(highestVersion, version);
            } else if (fileName.match(versionRegexNoUnderscore)) {
                var version = parseInt(fileName.match(/v(\d+)/)[1]);
                highestVersion = Math.max(highestVersion, version);
            }
        }
        
        return Math.max(highestVersion + 1, DEFAULT_VERSION);
    }

    function formatVersion(version) {
        return VERSION_PREFIX + padNumber(version, VERSION_PADDING);
    }

    function padNumber(number, width) {
        var numString = number.toString();
        while (numString.length < width) {
            numString = "0" + numString;
        }
        return numString;
    }

    function getVersionedFileName(folderPath, originalName) {
        var baseName = originalName;
        var extension = "";
        
        // Extract extension if exists
        var lastDotIndex = originalName.lastIndexOf(".");
        if (lastDotIndex !== -1) {
            baseName = originalName.substring(0, lastDotIndex);
            extension = originalName.substring(lastDotIndex);
        }
        
        // Remove any existing version numbers from baseName
        baseName = baseName.replace(/_v\d+$/, '').replace(/v\d+$/, '');
        
        // Check if any existing files use the v1 format
        var folder = new Folder(folderPath);
        var files = folder.getFiles();
        var useSimpleFormat = false;
        
        var versionRegexNoUnderscore = new RegExp(baseName.replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1") + "v\\d+");
        for (var i = 0; i < files.length; i++) {
            if (files[i].name.match(versionRegexNoUnderscore)) {
                useSimpleFormat = true;
                break;
            }
        }
        
        var version = getNextVersionNumber(folderPath, baseName);
        
        // Use the appropriate format based on existing files
        if (useSimpleFormat) {
            return baseName + "v" + version + extension;
        } else {
            return baseName + formatVersion(version) + extension;
        }
    }

    function setupRenderQueue(outputPath) {
        var comps = [];
        var selectedItems = app.project.selection;
        
        debugLog("Selected items: " + selectedItems.length);
        
        // Check if we have selected items in project panel
        if (selectedItems.length > 0) {
            // Use selected items
            for (var i = 0; i < selectedItems.length; i++) {
                if (selectedItems[i] instanceof CompItem) {
                    comps.push(selectedItems[i]);
                }
            }
        } else {
            // Use active composition if no selection
            var activeComp = app.project.activeItem;
            if (activeComp instanceof CompItem) {
                comps.push(activeComp);
            }
        }
        
        debugLog("Found " + comps.length + " compositions to render");
        
        for (var i = 0; i < comps.length; i++) {
            var renderQueueItem = app.project.renderQueue.items.add(comps[i]);
            var outputModule = renderQueueItem.outputModule(1);
            
            // Get versioned filename
            var versionedName = getVersionedFileName(outputPath.fsName, comps[i].name);
            var outputFile = new File(outputPath.fsName + "\\" + versionedName);
            
            debugLog("Setting output path for " + comps[i].name + ":\n" + outputFile.fsName);
            outputModule.file = outputFile;
        }
        
        return comps.length; // Return number of compositions added
    }

    function main() {
        // Check if there's either an active comp or selected items first
        var selectedItems = app.project.selection;
        var hasValidSelection = false;
        
        for (var i = 0; i < selectedItems.length; i++) {
            if (selectedItems[i] instanceof CompItem) {
                hasValidSelection = true;
                break;
            }
        }
        
        if (!hasValidSelection && !(app.project.activeItem instanceof CompItem)) {
            alert("No active composition found. Please select or open a composition first.");
            return;
        }
        
        var projectFolderPath = getProjectFolderPath();
        if (!projectFolderPath) return;
        
        var dailiesFolder = findDailiesFolder(projectFolderPath);
        if (!dailiesFolder) return;
        
        // Show dialog first
        var dialogResult = showDailiesDialog(dailiesFolder);
        if (!dialogResult) return;
        
        var targetFolder;
        
        if (dialogResult.isRegular) {
            // Regular date-based folder
            targetFolder = createDateFolder(dailiesFolder);
        } else {
            // Custom subfolder
            var dateFolder = createDateFolder(dailiesFolder);
            if (!dateFolder) return;
            
            if (dialogResult.useExistingFolder) {
                // Use existing folder
                targetFolder = new Folder(dateFolder.fsName + "\\" + dialogResult.customName);
                if (!targetFolder.exists) {
                    alert("Error: Selected folder no longer exists!");
                    return;
                }
            } else {
                // Create new folder
                targetFolder = createCustomFolder(dateFolder, dialogResult.customName);
            }
        }
        
        if (!targetFolder) return;
        
        // Add to render queue using active comp or selections
        setupRenderQueue(targetFolder);
    }

    main();
    
    app.endUndoGroup();
}
