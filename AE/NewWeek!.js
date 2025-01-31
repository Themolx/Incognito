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

        // Add preview of new path
        var previewGroup = dialog.add("group");
        previewGroup.orientation = "row";
        var previewLabel = previewGroup.add("statictext", undefined, "Preview: ");
        var previewPath = previewGroup.add("edittext", undefined, projPath);
        previewPath.preferredSize.width = 300;
        previewPath.enabled = false;

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

            // Add change listener to update preview
            tokenInput.onChange = function() {
                updatePathPreview();
            };
        }

        // Function to update path preview
        function updatePathPreview() {
            var previewPathStr = basePath;
            var remainingPath = projPath.substring(basePath.length);
            var currentWeekToken = getWeekToken(projPath);
            var newWeekToken = autoWeekCheck.value ? incrementWeekNumber(currentWeekToken) : null;
            
            for (var i = 0; i < tokenInputs.length; i++) {
                var tokenInfo = tokenInputs[i];
                if (tokenInfo.isWeek && autoWeekCheck.value) {
                    remainingPath = remainingPath.replace(tokenInfo.original, newWeekToken);
                } else if (tokenInfo.isVersion) {
                    remainingPath = remainingPath.replace(tokenInfo.original, resetVersion());
                } else if (tokenInfo.input.text !== tokenInfo.original) {
                    remainingPath = remainingPath.replace(tokenInfo.original, tokenInfo.input.text);
                }
            }
            
            previewPath.text = previewPathStr + remainingPath;
        }

        // Update week token input state when checkbox changes
        autoWeekCheck.onClick = function() {
            for (var i = 0; i < tokenInputs.length; i++) {
                if (tokenInputs[i].isWeek) {
                    tokenInputs[i].input.enabled = !autoWeekCheck.value;
                }
            }
            updatePathPreview();
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

    function updateCompNames(item, currentWeekToken, newWeekToken) {
        if (item instanceof CompItem) {
            var oldName = item.name;
            var newName = oldName;
            
            if (currentWeekToken && newWeekToken) {
                newName = newName.replace(currentWeekToken, newWeekToken);
            }
            
            if (newName !== oldName) {
                item.name = newName;
                // Update expressions in this comp and all comps that use this comp
                updateExpressionsInAllComps(oldName, newName);
            }
            
            // Process nested items
            for (var i = 1; i <= item.numItems; i++) {
                updateCompNames(item.item(i), currentWeekToken, newWeekToken);
            }
        } else if (item instanceof FolderItem) {
            for (var i = 1; i <= item.numItems; i++) {
                updateCompNames(item.item(i), currentWeekToken, newWeekToken);
            }
        }
    }

    function updateExpressionsInAllComps(oldName, newName) {
        var proj = app.project;
        for (var i = 1; i <= proj.numItems; i++) {
            var item = proj.item(i);
            if (item instanceof CompItem) {
                updateExpressions(item, oldName, newName);
            }
        }
    }

    function updateExpressions(comp, oldName, newName) {
        for (var i = 1; i <= comp.numLayers; i++) {
            var layer = comp.layer(i);
            scanAndUpdateExpressions(layer, oldName, newName);
        }
    }

    function scanAndUpdateExpressions(layer, oldName, newName) {
        try {
            // Recursive function to scan all properties
            function scanProperty(prop) {
                try {
                    // Check if this property has an expression
                    if (prop.canSetExpression && prop.expression) {
                        var expr = prop.expression;
                        if (expr.indexOf(oldName) !== -1) {
                            // Simple direct replacement of the name
                            prop.expression = expr.replace(new RegExp(oldName, 'g'), newName);
                        }
                    }

                    // If property has sub-properties, scan them
                    if (prop.propertyType === PropertyType.INDEXED_GROUP || 
                        prop.propertyType === PropertyType.NAMED_GROUP) {
                        for (var i = 1; i <= prop.numProperties; i++) {
                            scanProperty(prop.property(i));
                        }
                    }
                } catch (err) {
                    // Skip any properties that can't be accessed
                }
            }

            // Start scanning from the main property groups
            if (layer.effect) scanProperty(layer.effect);
            if (layer.transform) scanProperty(layer.transform);
            if (layer.mask) scanProperty(layer.mask);
            if (layer.text) scanProperty(layer.text);
            if (layer.materialOption) scanProperty(layer.materialOption);
            if (layer.geometryOption) scanProperty(layer.geometryOption);
            if (layer.audio) scanProperty(layer.audio);
            
            // Check layer source if it's a property group
            if (layer.source && layer.source.propertyType) {
                scanProperty(layer.source);
            }
        } catch (err) {
            // Skip any layers that can't be accessed
        }
    }

    // Create and show UI
    var dialog = buildUI(this);
    if (dialog instanceof Window) {
        dialog.center();
        dialog.show();
    }
}
