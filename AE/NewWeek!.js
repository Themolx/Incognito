{
    // New Week File Script
    // This script helps increment week numbers in project files and comp names
    
    function splitPathIntoTokens(path) {
        // Split path by common delimiters
        var tokens = path.split(/[\\\/\_\-\s]/);
        // Filter out empty tokens
        tokens = tokens.filter(function(token) { return token.length > 0; });
        
        // Find the index of "shots" token
        var shotsIndex = -1;
        for (var i = 0; i < tokens.length; i++) {
            if (tokens[i].toLowerCase() === "shots") {
                shotsIndex = i;
                break;
            }
        }
        
        // Return only tokens after "shots"
        return shotsIndex !== -1 ? tokens.slice(shotsIndex + 1) : tokens;
    }

    function getPathBeforeShots(path) {
        var shotsIndex = path.toLowerCase().indexOf("shots");
        if (shotsIndex !== -1) {
            var endIndex = path.indexOf("\\", shotsIndex);
            if (endIndex === -1) endIndex = path.indexOf("/", shotsIndex);
            return endIndex !== -1 ? path.substring(0, endIndex + 1) : path;
        }
        return "";
    }

    function resetVersion() {
        return "v1";
    }

    function buildUI(thisObj) {
        var dialog = (thisObj instanceof Panel) ? thisObj : new Window("dialog", "Path Token Editor");
        dialog.orientation = "column";
        dialog.alignChildren = ["left", "top"];
        dialog.spacing = 10;
        dialog.margins = 16;

        // Add project path display
        var proj = app.project;
        var projPath = proj.file ? proj.file.fsName : "";
        if (!projPath) {
            alert("Please save the project first!");
            return null;
        }

        // Display base path (up to shots)
        var basePath = getPathBeforeShots(projPath);
        var basePathGroup = dialog.add("group");
        basePathGroup.orientation = "row";
        var basePathText = basePathGroup.add("statictext", undefined, "Base Path: " + basePath);
        basePathText.enabled = false;

        // Add checkbox for auto week increment
        var weekGroup = dialog.add("group");
        weekGroup.orientation = "row";
        var autoWeekCheck = weekGroup.add("checkbox", undefined, "Auto Increment Week Number");
        autoWeekCheck.value = true; // Default to auto increment

        // Create scrollable area for tokens
        var scrollGroup = dialog.add("group");
        scrollGroup.orientation = "column";
        scrollGroup.alignChildren = ["left", "top"];
        scrollGroup.spacing = 5;
        scrollGroup.maximumSize.height = 400;
        
        var tokens = splitPathIntoTokens(projPath);
        var tokenInputs = [];

        // Create input fields for each token
        for (var i = 0; i < tokens.length; i++) {
            var token = tokens[i];
            var tokenGroup = scrollGroup.add("group");
            tokenGroup.orientation = "row";
            tokenGroup.spacing = 5;
            
            var tokenLabel = tokenGroup.add("statictext", undefined, token);
            tokenLabel.preferredSize.width = 100;
            
            var tokenInput = tokenGroup.add("edittext", undefined, token);
            tokenInput.preferredSize.width = 150;

            // Disable editing for week token if auto increment is on
            if (token.toLowerCase().match(/ww\d{2}/)) {
                tokenInput.enabled = !autoWeekCheck.value;
            }

            // Handle version token
            var isVersion = token.toLowerCase().match(/v\d+/);
            if (isVersion) {
                tokenInput.text = resetVersion();
                tokenInput.enabled = false;
            }
            
            tokenInputs.push({
                original: token,
                input: tokenInput,
                isWeek: token.toLowerCase().match(/ww\d{2}/) ? true : false,
                isVersion: isVersion ? true : false
            });
        }

        // Update week token input state when checkbox changes
        autoWeekCheck.onClick = function() {
            for (var i = 0; i < tokenInputs.length; i++) {
                if (tokenInputs[i].isWeek) {
                    tokenInputs[i].input.enabled = !autoWeekCheck.value;
                }
            }
        };

        // Add buttons
        var buttonGroup = dialog.add("group");
        buttonGroup.orientation = "row";
        var processButton = buttonGroup.add("button", undefined, "Process");
        var cancelButton = buttonGroup.add("button", undefined, "Cancel");

        // Handle button clicks
        processButton.onClick = function() {
            var basePath = getPathBeforeShots(projPath);
            var remainingPath = projPath.substring(basePath.length);
            var newPath = basePath;
            var changes = false;
            var currentWeekToken = getWeekToken(projPath);
            var newWeekToken = autoWeekCheck.value ? incrementWeekNumber(currentWeekToken) : null;
            
            // Replace tokens that were changed
            for (var i = 0; i < tokenInputs.length; i++) {
                var tokenInfo = tokenInputs[i];
                if (tokenInfo.isWeek && autoWeekCheck.value) {
                    remainingPath = remainingPath.replace(tokenInfo.original, newWeekToken);
                    changes = true;
                } else if (tokenInfo.isVersion) {
                    remainingPath = remainingPath.replace(tokenInfo.original, resetVersion());
                    changes = true;
                } else if (tokenInfo.input.text !== tokenInfo.original) {
                    remainingPath = remainingPath.replace(tokenInfo.original, tokenInfo.input.text);
                    changes = true;
                }
            }

            newPath += remainingPath;

            if (!changes) {
                alert("No changes were made to tokens.");
                return;
            }

            // Create new folder if needed
            var newFolder = new Folder(new File(newPath).parent);
            if (!newFolder.exists) {
                newFolder.create();
            }

            // Update compositions that contain changed tokens
            if (autoWeekCheck.value && currentWeekToken && newWeekToken) {
                for (var j = 1; j <= proj.numItems; j++) {
                    updateCompNames(proj.item(j), currentWeekToken, newWeekToken);
                }
            }

            for (var i = 0; i < tokenInputs.length; i++) {
                var tokenInfo = tokenInputs[i];
                if (!tokenInfo.isWeek && tokenInfo.input.text !== tokenInfo.original) {
                    for (var j = 1; j <= proj.numItems; j++) {
                        updateCompNames(proj.item(j), tokenInfo.original, tokenInfo.input.text);
                    }
                }
            }

            // Save project with new name
            var newFile = new File(newPath);
            proj.save(newFile);
            alert("Project saved with updated tokens!\nNew path: " + newPath);
            dialog.close();
        }

        cancelButton.onClick = function() {
            dialog.close();
        }

        dialog.layout.layout(true);
        dialog.layout.resize();
        dialog.center();
        
        return dialog;
    }

    function getWeekToken(path) {
        var weekRegex = /ww\d{2}/i;
        var match = path.match(weekRegex);
        return match ? match[0] : null;
    }

    function incrementWeekNumber(weekToken) {
        if (!weekToken) return null;
        
        var weekNum = parseInt(weekToken.substring(2));
        weekNum = (weekNum + 1) % 53; // Loop back to 1 after week 52
        if (weekNum === 0) weekNum = 1;
        
        return "ww" + (weekNum < 10 ? "0" : "") + weekNum;
    }

    function updateExpressions(comp, oldName, newName) {
        // Update expressions in all properties of all layers
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            
            // Go through all properties
            var props = layer.property("Effects");
            if (props) {
                for (var j = 1; j <= props.numProperties; j++) {
                    var effect = props.property(j);
                    for (var k = 1; k <= effect.numProperties; k++) {
                        var prop = effect.property(k);
                        if (prop.expression && prop.expression.indexOf(oldName) !== -1) {
                            prop.expression = prop.expression.replace(new RegExp(oldName, 'g'), newName);
                        }
                    }
                }
            }
            
            // Check transform properties
            var transform = layer.transform;
            for (var j = 1; j <= transform.numProperties; j++) {
                var prop = transform.property(j);
                if (prop.expression && prop.expression.indexOf(oldName) !== -1) {
                    prop.expression = prop.expression.replace(new RegExp(oldName, 'g'), newName);
                }
            }
        }
    }

    function updateCompNames(item, currentWeekToken, newWeekToken) {
        if (item instanceof CompItem) {
            var oldName = item.name;
            // Update composition name if it contains the week token
            if (item.name.toLowerCase().indexOf(currentWeekToken.toLowerCase()) !== -1) {
                var newName = item.name.replace(new RegExp(currentWeekToken, 'gi'), newWeekToken);
                item.name = newName;
                
                // Update expressions in all comps that might reference this comp
                for (var i = 1; i <= app.project.numItems; i++) {
                    var comp = app.project.item(i);
                    if (comp instanceof CompItem) {
                        updateExpressions(comp, oldName, newName);
                    }
                }
            }
            
            // Search through all layers in the composition
            for (var i = 1; i <= item.numLayers; i++) {
                var layer = item.layer(i);
                if (layer.source instanceof CompItem) {
                    updateCompNames(layer.source, currentWeekToken, newWeekToken);
                }
            }
        }
    }

    function processWeekIncrement() {
        var proj = app.project;
        if (!proj) return alert("No project is open!");

        // Get project file path
        var projPath = proj.file ? proj.file.fsName : "";
        if (!projPath) return alert("Please save the project first!");

        // Extract current week token
        var currentWeekToken = getWeekToken(projPath);
        if (!currentWeekToken) return alert("No week token found in project path!");

        // Generate new week token
        var newWeekToken = incrementWeekNumber(currentWeekToken);
        if (!newWeekToken) return alert("Failed to increment week number!");

        // Create new folder path
        var newPath = projPath.replace(new RegExp(currentWeekToken, 'gi'), newWeekToken);
        var newFolder = new Folder(new File(newPath).parent);
        if (!newFolder.exists) {
            newFolder.create();
        }

        // Recursively update all compositions
        for (var i = 1; i <= proj.numItems; i++) {
            updateCompNames(proj.item(i), currentWeekToken, newWeekToken);
        }

        // Save project with new name
        var newFile = new File(newPath);
        proj.save(newFile);
        alert("Project saved with incremented week number!\nNew path: " + newPath);
    }

    // Create and show UI
    var dialog = buildUI(this);
    if (dialog instanceof Window) {
        dialog.center();
        dialog.show();
    }
}
