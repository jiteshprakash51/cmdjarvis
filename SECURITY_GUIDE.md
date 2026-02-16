# CMDJARVIS Security Guide

## Security Improvements Implemented

This guide explains the security measures in place to protect your passwords and API keys from unauthorized access.

---

## 1. **API Key Encryption**

### What Changed

- **Before**: API keys were stored in **plaintext** in `jarvis_user.json`
- **After**: API keys are now **encrypted** before storage

### How It Works

- Your API key is encrypted using **Fernet (AES-128)** from the `cryptography` library
- The encryption key is derived from your **login password** using **PBKDF2** with 100,000 iterations
- This means only someone who knows your password can decrypt the API key

### Security Benefit

If someone gains access to the `jarvis_user.json` file:

- ❌ They **cannot** see your API key in plaintext
- ❌ They **cannot** decrypt it without your password
- ✅ Your API key remains protected

---

## 2. **Password Security**

### Storage Method

Passwords are **never stored** - instead we store a **cryptographic hash**:

- Algorithm: **PBKDF2-SHA256** with 200,000 iterations
- Each password has a unique **salt** to prevent rainbow table attacks
- Comparison uses **constant-time comparison** to prevent timing attacks

### Why This is Safe

- Even if someone gets the hash, they **cannot reverse it** to get the password
- A strong password cannot be easily guessed from the hash
- Rainbow tables and brute force attacks are computationally infeasible

---

## 3. **File Permissions (Windows)**

### Windows NTFS Security

When credentials are saved, file permissions are automatically set:

- **Owner (You)**: Read + Write access
- **Everyone else**: No access

**Command equivalent**:

```powershell
icacls jarvis_user.json /grant "%USERNAME%:F" /inheritance:r
```

This means:

- ✅ Only your Windows user account can read/modify the file
- ❌ Other users on the same laptop **cannot** access or view the file
- ❌ Administrator accounts cannot bypass NTFS permissions easily

### Verify File Permissions:

Open PowerShell and run:

```powershell
icacls jarvis_user.json
```

You should see something like:

```
jarvis_user.json YOUR_USERNAME:(F)
             BUILTIN\Administrators:(F)
```

---

## 4. **Secure File Deletion**

### When You Reset Credentials

- Files are overwritten with random data **before deletion**
- This prevents recovery via file undelete utilities
- Prevents sector-level forensic recovery

---

## 5. **What's NOT Stored in the File**

The `jarvis_user.json` file contains:

- ✅ Encrypted API key
- ✅ Password hash
- ✅ Password salt

It does **NOT** contain:

- ❌ Your plaintext password
- ❌ Your plaintext API key
- ❌ Any personal information

**File example** (encrypted):

```json
{
  "api_key": "gAAAAABlxyz...[encrypted]...QWE=",
  "password_hash": "abcd1234...[hashed]...",
  "password_salt": "xyz789...[unique salt]..."
}
```

---

## 6. **Multi-User Laptop Security**

### Scenario: Other Users on Same Laptop

**What they can do:**

- ❌ See the `jarvis_user.json` file exists (if in a shared folder)
- ❌ View the encrypted API key
- ❌ Decrypt it without your password
- ❌ Use your API key

**Why they can't:**

1. **File Permissions**: Windows denies read access unless you grant it
2. **Encryption**: Even if they copy the file, encryption key is password-protected
3. **Password Hash**: They cannot reverse-engineer your password from the hash

### Best Practices

- Store `jarvis_user.json` in your **user-specific folder** (e.g., `C:\Users\YourUsername\...`)
- **Never share** your password with anyone
- Use a **strong password** (12+ characters, mix of letters/numbers/symbols)
- Log out properly when done

---

## 7. **Password Change Security**

When you change your password:

1. Current password is verified ✓
2. **Old API key is decrypted** using the old password
3. **New encryption key is derived** from the new password
4. **API key is re-encrypted** with the new key
5. **Password hash is updated**
6. **File permissions are reset**

### Why This Matters

- Changing your password doesn't invalidate your API key
- Your encrypted API key becomes "locked" to your new password
- Old password cannot decrypt the file anymore

---

## 8. **Attack Prevention**

### Attack: Brute Force Password

- **Protected by**: PBKDF2 with 200,000 iterations
- **Protection**: Takes ~1-2 seconds per attempt (infeasible for millions of attempts)

### Attack: Rainbow Tables / Dictionary Attack

- **Protected by**: Unique salt per user
- **Protection**: Pre-computed tables are useless; attacker must compute hash for each salt

### Attack: API Key Theft

- **Protected by**: AES-128 Fernet encryption
- **Protection**: Encryption is industry-standard; key is password-protected

### Attack: File Copy / USB Theft

- **Protected by**: NTFS permissions + encryption
- **Protection**: File is inaccessible to other users; encrypted data is useless without password

### Attack: Memory Inspection

- **Protected by**: Passwords are read via `getpass` and never stored after verification
- **Protection**: API key only held in memory during session; cleared on exit

---

## 9. **Additional Security Recommendations**

### 1. **Use a Strong Password**

```
Good:     MyDog$42Lives2024!
Bad:      password123
Bad:      12345678
```

### 2. **Update OpenRouter API Key Regularly**

- Rotate your API key periodically
- Use `change api key` command
- Invalidate old keys in OpenRouter dashboard

### 3. **Secure Your Windows Account**

- Use a strong Windows password
- Enable Windows Defender
- Keep Windows updated
- Use PIN login instead of password if possible

### 4. **Backup Your Credentials Securely**

- If you lose your laptop, your credentials are lost (this is intentional)
- Store backup API keys in a password manager (like Bitwarden, 1Password)
- Consider enabling Windows Backup with encryption

### 5. **Monitor File Access**

Check file modification timestamp:

```powershell
Get-Item jarvis_user.json | Select-Object LastWriteTime
```

### 6. **Use Windows Encryption (BitLocker)**

For maximum security on Windows 10/11 Pro/Enterprise:

```powershell
# Enable BitLocker on C: drive
manage-bde -on C:
```

---

## 10. **Technical Details**

### Encryption Specifications

- **Algorithm**: Fernet (AES-128-CBC with HMAC)
- **Key Derivation**: PBKDF2-SHA256, 100,000 iterations
- **Encoding**: Base64 URL-safe encoding

### Password Hashing Specifications

- **Algorithm**: PBKDF2-HMAC-SHA256
- **Iterations**: 200,000
- **Salt Size**: 16 bytes (random per user)
- **Hash Size**: 32 bytes
- **Comparison**: Constant-time HMAC comparison

### File Permissions (Windows)

- **Owner**: Full Control (Read, Write, Modify, Delete)
- **Others**: No Access
- **Inherited Permissions**: Disabled (isolated)

---

## 11. **Troubleshooting**

### Problem: Can't Read File Permissions

**Error**: `Access Denied` when running `icacls`

**Solution**:

```powershell
# Run PowerShell as Administrator
$file = "jarvis_user.json"
$acl = Get-Acl $file
$acl | Format-List
```

### Problem: File Permissions Keep Resetting

**Cause**: Different drive (USB, network share) may not support NTFS ACLs

**Solution**: Store `jarvis_user.json` on your main C: drive in a local folder

### Problem: Can't Remember Password

**Solution**:

1. Run `factory reset` to delete credentials
2. Set up new password and API key
3. Store in password manager going forward

---

## 12. **Compliance & Standards**

This implementation follows:

- ✅ OWASP Password Storage Cheat Sheet
- ✅ NIST Password Guidelines
- ✅ CWE-327 (Use of Broken Cryptography)
- ✅ CWE-798 (Hardcoded Credentials - prevented)
- ✅ CWE-256 (Unencrypted Sensitive Data - prevented)

---

## Questions?

For more information about the cryptography library:

- https://cryptography.io/en/latest/
- https://en.wikipedia.org/wiki/Fernet_(cryptography)

For Windows security:

- https://docs.microsoft.com/en-us/windows/security/
- https://bitlocker.securemydevice.com/

---

**Last Updated**: February 16, 2026  
**Security Version**: 2.0 (Encrypted API Keys)
