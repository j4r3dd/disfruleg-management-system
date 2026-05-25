# UbicuoAI - Integration Guide

## ✅ Module Successfully Integrated

UbicuoAI has been successfully integrated into the DISFRULEG system and can now be launched from the module launcher!

## 🚀 How to Access

### From the Main Menu

1. **Login** to the DISFRULEG system
2. Go to the **Module Launcher** (main menu)
3. Look for the **"Ubicuo AI"** module card
   - **Color**: Purple (#9C27B0)
   - **Description**: "Procesamiento inteligente de pedidos con aprendizaje automático"
4. Click on the module card to launch

### Module Properties

- **Title**: Ubicuo AI
- **Module Key**: `ubicuoai`
- **Requires Admin**: `False` (accessible to all users)
- **Color Scheme**: Purple theme

## 📋 What Happens When You Launch

1. **Automatic Initialization**:
   - Checks if user is authenticated
   - Connects to database
   - Loads all products from database
   - Loads learning corrections from `ubicuoai_learning` table
   - Shows initialization summary

2. **Window Opens**:
   - Main UbicuoAI interface appears
   - Statistics displayed at top
   - Text area ready for order input

## 🔧 Technical Details

### Files Modified

1. **`src/ui/module_launcher.py`**
   - Added ubicuoai to module definitions (line ~171)
   - Added to module_functions map (line ~492)

2. **`launch_module.py`**
   - Added `launch_ubicuoai_module()` function (line ~348)
   - Added to main() routing (line ~427)

### Launch Flow

```
User clicks "Ubicuo AI" button
    ↓
ModuleLauncher.launch_module('ubicuoai')
    ↓
launch_module.launch_ubicuoai_module()
    ↓
open_ubicuoai_window(parent)
    ↓
initialize_ubicuoai() [if not initialized]
    ↓
UbicuoAI window opens
```

## 🎯 Usage Example

```python
# Manual launch (for testing)
from src.modules.ubicuoai import open_ubicuoai_window
import customtkinter as ctk

root = ctk.CTk()
window = open_ubicuoai_window(root)
root.mainloop()
```

## 📊 Features Available

1. **Parse Orders**: Paste WhatsApp orders and extract products
2. **Fuzzy Matching**: Find products even with spelling errors
3. **Learning System**: Correct products and system learns
4. **Suggestions**: Get multiple suggestions for unclear products
5. **Statistics**: View matching statistics and confidence levels

## 🔒 Requirements

- ✅ User must be logged in
- ✅ Database connection active
- ✅ `rapidfuzz` or `fuzzywuzzy` installed (already in requirements.txt)
- ✅ Products must be active in database
- ✅ `ubicuoai_learning` table auto-created on first run

## 🐛 Troubleshooting

### "No authenticated database connection"
**Solution**: Make sure user is logged in before opening the module

### "Products not loaded"
**Solution**: Check that products exist in database and are marked as active

### Module doesn't appear in launcher
**Solution**:
1. Restart the application
2. Check that `module_launcher.py` was updated correctly
3. Check console for errors

### Window doesn't open
**Solution**:
1. Check console for error messages
2. Verify database connection is working
3. Check that all dependencies are installed

## 📝 Next Steps

1. **Test the Module**:
   - Login and launch from menu
   - Test with sample orders
   - Train the learning system

2. **Integration with Receipt Generator**:
   - Connect "Send to Receipt Generator" button
   - Map matched products to receipt items

3. **Training**:
   - Use real orders
   - Correct misspellings
   - Build learning dictionary

## 🎨 Icon (Optional)

If you want to add a custom icon for the module:

1. Create/find an icon image
2. Name it `ubicuoai.png`
3. Place in the icons directory
4. The module card will automatically use it

## ✅ Integration Checklist

- [x] Module added to `module_launcher.py` definitions
- [x] Launch function added to `launch_module.py`
- [x] Module added to function map
- [x] Module added to main() routing
- [x] Clean architecture implemented
- [x] Database integration working
- [x] Documentation created
- [x] No admin requirement (accessible to all)

## 🎉 Ready to Use!

The module is now fully integrated and ready to use from the main menu!

**Enjoy using Ubicuo AI!** 🤖✨
