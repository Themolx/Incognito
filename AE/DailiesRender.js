/*
Auto-versioning Render Queue Setup Script v1.1
This script:
1. Finds project folder path based on project token pattern
2. Locates dailies folder in project structure
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

    function getProjectFolderPath() {
        var projectPath = app.project.file.path;
        
        var pathParts = projectPath.split(/[\\\/]/);
        var projectIndex = -1;
        
        for (var i = 0; i < pathParts.length; i++) {
            if (pathParts[i].match(/[A-Z]+_[A-Z]+_\d+/)) {
                projectIndex = i;
                break;
            }
        }
        
        if (projectIndex === -1) {
            return null;
        }
        
        var projectFolderPath = pathParts.slice(0, projectIndex + 1).join('/');
        return projectFolderPath;
    }

    function findDailiesFolder(projectFolderPath) {
        var outputFolder = new Folder(projectFolderPath + "/output");
        
        if (!outputFolder.exists) {
            return null;
        }
        
        var dailiesWithUnderscore = new Folder(outputFolder.fsName + "/_dailies");
        var dailiesWithoutUnderscore = new Folder(outputFolder.fsName + "/dailies");
        
        if (dailiesWithUnderscore.exists) {
            return dailiesWithUnderscore;
        } else if (dailiesWithoutUnderscore.exists) {
            return dailiesWithoutUnderscore;
        }
        
        return null;
    }

    function createDateFolder(parentFolder) {
        var date = new Date();
        var dateString = date.getFullYear().toString().substr(-2) +
                        ("0" + (date.getMonth() + 1)).slice(-2) +
                        ("0" + date.getDate()).slice(-2);
        
        var newFolder = new Folder(parentFolder.fsName + "/" + dateString);
        
        if (!newFolder.exists) {
            newFolder.create();
        }
        return newFolder;
    }

    function getNextVersionNumber(folderPath, baseName) {
        var folder = new Folder(folderPath);
        var files = folder.getFiles();
        var highestVersion = 0;
        
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
        
        return highestVersion + 1;
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
        
        var lastDotIndex = originalName.lastIndexOf(".");
        if (lastDotIndex !== -1) {
            baseName = originalName.substring(0, lastDotIndex);
            extension = originalName.substring(lastDotIndex);
        }
        
        baseName = baseName.replace(/_v\d+$/, '').replace(/v\d+$/, '');
        
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
        
        if (useSimpleFormat) {
            return baseName + "v" + version + extension;
        } else {
            return baseName + formatVersion(version) + extension;
        }
    }

    function setupRenderQueue(outputPath) {
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
            
            var versionedName = getVersionedFileName(outputPath.fsName, comps[i].name);
            var outputFile = new File(outputPath.fsName + "/" + versionedName);
            
            outputModule.file = outputFile;
        }
    }

    function main() {
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
    }

    main();
    
    app.endUndoGroup();
}
