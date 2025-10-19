# MiniDapp Structure Guide

## Complete MiniDapp Package Requirements

A properly structured MiniDapp must include these essential files for successful deployment on Minima.

## Required Files

### 1. `dapp.conf` (Required)
Configuration file that defines your MiniDapp metadata.

```json
{
  "name": "MyMiniDapp",
  "version": "1.0.0",
  "description": "My awesome MiniDapp",
  "icon": "icon.png",
  "category": "Utility",
  "browser": "index.html"
}
```

### 2. `mds.js` (CRITICAL - Must be included!)

**This is the most important requirement!**

The `mds.js` file is the **MDS client library** that allows your MiniDapp to communicate with the Minima blockchain. Without it, your MiniDapp will fail with `ERR_BLOCKED_BY_ORB` errors.

#### Why mds.js Must Be Inside Your Package

- The file from `~/.minima/1.0/mds/mds.js` is the **MDS server**, not the client library
- Loading from file system paths is blocked by browser security (ORB - Opaque Response Blocking)
- The client library **must be bundled inside** your `.mds.zip` package
- You cannot load it from external URLs or file system paths

#### How to Get mds.js

Download from one of these sources:

**Option 1: Direct Download (Recommended)**
```bash
curl -o mds.js https://raw.githubusercontent.com/minima-global/Minima/master/mds/mds.js
```

**Option 2: From GitHub Releases**
Visit https://github.com/minima-global/Minima/releases and download `mds-2.1.0.js` (or latest version)

**Option 3: Copy from Minima Installation**
If you have Minima installed, the file is located at:
- Linux/Mac: `~/.minima/mds/webroot/mds.js`
- Windows: `%USERPROFILE%\.minima\mds\webroot\mds.js`

### 3. `index.html` (Required)
Your MiniDapp's main entry point.

**CRITICAL: Load mds.js FIRST, before any other scripts!**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My MiniDapp</title>

    <!-- MUST LOAD MDS.JS FIRST! -->
    <script type="text/javascript" src="./mds.js"></script>

    <!-- Then load your custom scripts -->
    <script type="text/javascript" src="./app.js"></script>
    <link rel="stylesheet" href="./style.css">
</head>
<body>
    <div id="app">
        <h1>My MiniDapp</h1>
        <div id="status">Connecting to Minima...</div>
    </div>

    <script>
        // Initialize MDS connection
        MDS.init(function(msg) {
            console.log('MDS Message:', msg);

            if(msg.event === "inited") {
                document.getElementById('status').textContent = 'Connected!';

                // Now you can use MDS commands
                MDS.cmd("status", function(response) {
                    console.log('Node status:', response);
                });
            }
        });
    </script>
</body>
</html>
```

### 4. Additional Files (Optional but Recommended)

- `style.css` - Your styles
- `app.js` - Your JavaScript code
- `icon.png` - App icon (referenced in dapp.conf)
- `images/` - Any images or assets
- Other HTML pages, libraries, etc.

## Complete MiniDapp Structure Example

```
MyMiniDapp/
├── dapp.conf          # Configuration (required)
├── mds.js             # MDS client library (REQUIRED!)
├── index.html         # Main entry point (required)
├── app.js             # Your JavaScript logic
├── style.css          # Your styles
├── icon.png           # App icon
└── assets/            # Additional resources
    ├── logo.png
    └── data.json
```

## Common Mistakes to Avoid

### ❌ DON'T: Load mds.js from CDN or external URL
```html
<!-- THIS WILL NOT WORK IN PRODUCTION! -->
<script src="https://docs.minima.global/mds.js"></script>
```

### ❌ DON'T: Load mds.js from file system
```html
<!-- THIS WILL FAIL WITH ERR_BLOCKED_BY_ORB! -->
<script src="file:///C:/Users/.../.minima/1.0/mds/mds.js"></script>
```

### ❌ DON'T: Forget to include mds.js in your package
```
MyMiniDapp/
├── dapp.conf
├── index.html         # Even if HTML references mds.js...
└── app.js             # ...it won't work if file is missing!
```

### ✅ DO: Include mds.js inside your MiniDapp package
```
MyMiniDapp/
├── dapp.conf
├── mds.js             # ✓ File is physically present
├── index.html         # ✓ References ./mds.js
└── app.js
```

### ✅ DO: Use relative path in HTML
```html
<!-- Correct way -->
<script src="./mds.js"></script>
```

## Packaging Your MiniDapp

### Using Minima MCP

```python
from minima_mcp.server import package_minidapp

# The tool will warn you if mds.js is missing!
result = package_minidapp(
    project_path="./MyMiniDapp"
)

if result["warnings"]:
    for warning in result["warnings"]:
        print(warning)
```

### Manual Packaging

1. Ensure all files are in project directory (including `mds.js`!)
2. Select all files (not the folder)
3. Create ZIP archive
4. Rename to `yourapp.mds.zip`

```bash
# Linux/Mac
cd MyMiniDapp
zip -r ../MyMiniDapp.mds.zip .

# Verify mds.js is included
unzip -l ../MyMiniDapp.mds.zip | grep mds.js
```

## Installing Your MiniDapp

### Using MCP
```python
from minima_mcp.server import install_packaged_minidapp

result = install_packaged_minidapp(
    zip_path="/path/to/MyMiniDapp.mds.zip"
)
```

### Using Minima Terminal
```bash
mds action:install file:/absolute/path/to/MyMiniDapp.mds.zip
```

### Using Minima Hub
1. Open Minima Hub in browser: `http://localhost:9003`
2. Go to MiniDapps section
3. Click "Install" and select your `.mds.zip` file

## Accessing Your MiniDapp

After installation:
```
https://localhost:9003/YOUR_MINIDAPP_UID/
```

Get your UID:
```bash
mds
```

## Troubleshooting

### Error: ERR_BLOCKED_BY_ORB

**Cause:** mds.js is not included in your package or is being loaded from wrong location

**Solution:**
1. Download mds.js from GitHub
2. Place it in your project root
3. Update HTML to use `<script src="./mds.js"></script>`
4. Repackage and reinstall

### Error: MDS is not defined

**Cause:** mds.js loaded after your code tried to use it

**Solution:**
1. Move `<script src="./mds.js"></script>` to the TOP of your `<head>` section
2. Ensure MDS.init() is called before any MDS commands

### Error: Cannot read property 'init' of undefined

**Cause:** mds.js failed to load or loaded incorrectly

**Solution:**
1. Check browser console for loading errors
2. Verify mds.js exists in package: `unzip -l yourapp.mds.zip | grep mds.js`
3. Verify mds.js content is valid JavaScript (not HTML error page)

## MDS API Basics

Once mds.js is loaded correctly:

```javascript
// Initialize connection
MDS.init(function(msg) {
    if(msg.event === "inited") {
        console.log("Connected to Minima!");

        // Execute commands
        MDS.cmd("status", function(resp) {
            if(resp.status) {
                console.log("Chain:", resp.response.chain);
            }
        });

        // Listen for events
        MDS.notify("NEWBLOCK", function(data) {
            console.log("New block:", data);
        });
    }
});
```

### Common MDS Commands

```javascript
// Get node status
MDS.cmd("status", callback);

// Get balance
MDS.cmd("balance", callback);

// Send transaction
MDS.cmd("send amount:10 address:0x123...", callback);

// Get coins
MDS.cmd("coins", callback);
```

## Best Practices

1. **Always include mds.js** - It's the most critical file!
2. **Load mds.js first** - Before any other scripts
3. **Use relative paths** - `./mds.js` not absolute paths
4. **Test locally first** - Use a development Minima node
5. **Check file sizes** - MiniDapps should be < 10MB typically
6. **Validate package** - Unzip and inspect before installing

## Resources

- [Minima GitHub](https://github.com/minima-global/Minima)
- [MDS Documentation](https://docs.minima.global)
- [Minima Community](https://minima.global/community)
- [Example MiniDapps](https://github.com/minima-global/MiniDapps)

## Using Minima MCP for Development

The Minima MCP provides automated tools with built-in validation:

```python
# Create new project (includes template with proper structure)
result = create_minidapp_project(
    name="MyApp",
    description="My awesome MiniDapp",
    output_dir="./projects"
)

# Write files
write_minidapp_file(
    project_path="./projects/MyApp",
    file_name="app.js",
    content="// Your code here"
)

# Package with validation (warns about missing mds.js!)
result = package_minidapp(
    project_path="./projects/MyApp"
)

# Install automatically
result = install_packaged_minidapp(
    zip_path=result["data"]["zip_path"]
)
```

The MCP will automatically warn you if `mds.js` is missing from your project!
