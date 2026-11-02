# Publishing on GitHub

The page shown in the screenshot is **Projects**, a planning board. It is not a
code repository. Use **Repositories → New repository**.

## Create the repository

1. Open GitHub.
2. Select **Repositories**.
3. Select **New repository**.
4. Name it, for example `cezanne-unlock-research`.
5. Choose Public only after checking the privacy scan below.
6. Do not initialize with a README if the local folder already has one.
7. Create the repository.

## Upload only the public folder

Only the contents of the `github/` directory should be uploaded. Do not upload
the parent research workspace, which contains firmware, boot images, seccfg,
preloader dumps, APKs, and raw logs.

From a terminal:

```text
cd github
git init
git add .
git commit -m "Document verified cezanne unlock and root research"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

Do not paste an authentication token into a public command, issue, log, or
screenshot.

## Pre-publication privacy scan

Search for:

- Windows user profile paths;
- IMEI;
- MEID;
- SOCID;
- UFS CID/serial;
- phone serial numbers;
- private IP addresses;
- Wi-Fi credentials;
- GitHub/API tokens.

The provided `.gitignore` excludes firmware, partition images, platform tools,
APKs, executables, raw logs, and screenshots.

## Before pushing

Run:

```text
git status
git diff --cached --stat
Get-ChildItem -Recurse -File | Sort-Object Length -Descending | Select-Object -First 20
```

Do not push a file merely because it is text: raw logs can contain unique IDs.

## License

Choose a license before publication. If scripts substantially derive from
`mtkclient`, use a compatible GPLv3 approach and retain upstream attribution.
Do not include vendor firmware or Magisk APKs in the repository.

