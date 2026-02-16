# CMDJARVIS Security Update - Setup Instructions

## What Changed

Your CMDJARVIS application has been updated with **military-grade encryption** for API keys and improved security features. This prevents other users on your computer from accessing your credentials.

---

## Installation Steps

### Step 1: Install New Dependency

Run this command in PowerShell or CMD:

```powershell
pip install -r requirements.txt
```

This will install:

- `cryptography` (for encryption)
- All other existing dependencies

### Step 2: What to Expect on First Run

**If you have existing credentials:**

- Your old plaintext API key will be **lost** (this is intentional for security)
- You'll need to set up new credentials on first run
- You can use the same API key from OpenRouter

**If you're a new user:**

- Setup works exactly the same as before
- Your password encrypts the API key automatically

### Step 3: Test the Installation

Run JARVIS normally:

```powershell
python main.py
```

Follow the setup or login prompts.

---

## File Permissions (Windows)

After credentials are saved, the `jarvis_user.json` file is automatically set with **strict permissions**:

### Verify Permissions:

```powershell
icacls jarvis_user.json
```

### Expected Output:

```
jarvis_user.json YOUR_USERNAME:(F)
             BUILTIN\Administrators:(F)
```

This means:

- ✅ Only YOU can open the file
- ❌ Other user accounts on the laptop cannot access it
- ❌ Even they copy the file, the API key is encrypted

---

## Security Features Summary

| Feature                 | Details                                        |
| ----------------------- | ---------------------------------------------- |
| **API Key Encryption**  | AES-128 (Fernet) - password protected          |
| **Password Storage**    | PBKDF2-SHA256, 200,000 iterations, unique salt |
| **File Permissions**    | NTFS-restricted to owner only                  |
| **Secure Deletion**     | Files overwritten before deletion              |
| **Password-Locked Key** | API key encryption key derived from password   |

---

## Command Reference

### Change API Key

```
You> change api key
```

- Prompted for current password
- Validates new key with OpenRouter
- Re-encrypts with current password

### Change Password

```
You> change password
```

- Prompts for current password
- API key is decrypted & re-encrypted with new password
- Password hash is updated

### Factory Reset

```
You> factory reset
```

- Securely deletes `jarvis_user.json`
- Overwrites file with random data
- Cannot be recovered

---

## Troubleshooting

### Error: "cryptography module not found"

**Solution**: Run `pip install cryptography`

### Error: "Failed to decrypt API key"

**Cause**: Password changed outside of JARVIS or file corrupted
**Solution**: Run `factory reset` and set up with new credentials

### Error: "Access Denied" on jarvis_user.json

**Cause**: File permissions issue or drive doesn't support NTFS
**Solution**: Store file on C: drive in user folder, not USB/network

### Existing Users: API Key Lost

**Expected behavior** - The old plaintext API key cannot be read by the new system
**Solution**: Set it again using `change api key` command (or first-run setup)

---

## For Existing Users (Migration)

If you already have `jarvis_user.json` from before:

1. Note your current **API key** (stored in OpenRouter account)
2. Delete the old `jarvis_user.json`
3. Run JARVIS - it will ask for setup
4. Enter your API key again (same one is fine)
5. Create new password

---

## Questions or Issues?

1. See **SECURITY_GUIDE.md** for detailed technical information
2. Check file permissions with: `icacls jarvis_user.json`
3. Review encryption implementation in `utils/user_store.py`

---

## Key Points

✅ **Your passwords & API keys are now encrypted**
✅ **Other users cannot access your credentials**
✅ **File is locked to your Windows user account**
✅ **Password protects the API key**
✅ **No plaintext secrets stored**

**Enjoy secure command execution!** 🔐

---

**Version**: 2.0 Secure  
**Last Updated**: February 16, 2026
