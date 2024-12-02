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

    function createDateFolder(parentFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        ("0" + (date.getMonth() + 1)).slice(-2) +
                        ("0" + date.getDate()).slice(-2);
        
        var newFolder = new Folder(parentFolder.fsName + "\\" + dateString);
        debugLog("DATE FOLDER PATH: " + newFolder.fsName);
        
        if (!newFolder.exists) {
            var created = newFolder.create();
            debugLog("CREATED? " + created);
            if (!created) {
                alert("ERROR: Failed to create date folder!");
                return null;
            }
        }
        return newFolder;
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
        var selectedItems = app.project.selection;
        var comps = [];
        
        debugLog("Selected items: " + selectedItems.length);
        
        for (var i = 0; i < selectedItems.length; i++) {
            if (selectedItems[i] instanceof CompItem) {
                comps.push(selectedItems[i]);
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
    }

    function main() {
        debugLog("=== STARTING ===");
        
        var projectFolderPath = getProjectFolderPath();
        if (!projectFolderPath) {
            return;
        }
        
        var dailiesFolder = findDailiesFolder(projectFolderPath);
        if (!dailiesFolder) {
            return;
        }
        
        var dateFolder = createDateFolder(dailiesFolder);
        if (!dateFolder) {
            return;
        }
        
        setupRenderQueue(dateFolder);
        
        debugLog("=== COMPLETE ===\nOutput path: " + dateFolder.fsName);
    }

    main();
    
    app.endUndoGroup();
}
