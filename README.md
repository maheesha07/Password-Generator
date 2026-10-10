# SecurePass — Password Generator + Encrypted Password Vault

A local-first browser-based student portfolio project. Includes the original secure password generator and an encrypted login vault.

## Run

Requires a modern browser and a secure context for Web Crypto. In this directory, run:

```sh
python -m http.server 8000
```

Then open http://localhost:8000. No Python packages or backend are required. Can be hosted via HTTPS (for example GitHub Pages), but browser storage is **per browser and origin**.

## Features

- Password generator: length 4–128, four character types, exclude similar characters, strength estimate, copy, recent five in-memory history.
- Vault: create/unlock with master password; add/search/edit/delete logins; generate passwords inside form; copy credentials; lock.
- AES-256-GCM authenticated encryption with random IV for each save; PBKDF2-SHA256 with 600,000 iterations and a unique random salt. Master password is not saved. Cryptographic key and decrypted items are held in browser memory while unlocked.
- Encrypted JSON backup export/import. Import replaces the existing local vault after confirmation.

## Important safety limitations

This is a **learning/demo application, NOT a professionally audited password manager**. Do not rely on it as your only copy of important credentials. Encryption does not protect against browser extensions, compromised devices, malicious injected JavaScript, or someone accessing your unlocked session. The vault remains unlocked until you click Lock or close/reload the page (no idle auto-lock). Browser data clearing, private mode, or moving domains/devices can erase access to the locally stored vault. Backups must be exported manually and stored securely. There is no master-password recovery or synchronization.

The browser's localStorage contains only an encrypted vault JSON record (salt, IV, ciphertext and algorithm metadata), but login data is decrypted in memory while unlocked. Clipboard copying may leave a password in clipboard history. The strength meter is a simple estimate, not a formal password audit.
