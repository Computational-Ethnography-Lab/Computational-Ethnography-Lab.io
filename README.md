Public page for Computational-Ethnography-Lab at https://github.com/Computational-Ethnography-Lab

Serves https://computationalethnography.org (see `CNAME`).

## Do not hand-edit `index.md`

`index.md` is a copy of
[`profile/README.md`](https://github.com/Computational-Ethnography-Lab/.github/blob/main/profile/README.md)
in the `.github` repository, which is the single source of truth for lab
landing-page content.

To change what appears on the website, edit that file and copy it here:

```bash
curl -fsSL https://raw.githubusercontent.com/Computational-Ethnography-Lab/.github/main/profile/README.md -o index.md
```

Editing `index.md` directly causes the website to drift out of sync with the
GitHub org landing page — the two had diverged substantially before August 2026.

Image paths resolve because `images/` here carries the same filenames as
`profile/images/` in the `.github` repository. Keep them in step when adding
images.
