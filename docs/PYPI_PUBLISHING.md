# Publishing RMTI v0.1.0 to PyPI (owner action required)

The repository contains `.github/workflows/publish-pypi.yml`. It has a **manual** trigger only. It rebuilds the immutable source at Git tag `v0.1.0` and checks that it resolves to commit `a79cebbdd4bfac4afa083c24ee01c554e6d29393`. The package identity, version, MIT metadata and distribution integrity are checked before upload. No password or API token is stored in GitHub.

## 1. Configure the GitHub environment

Open GitHub repository **Settings → Environments**. Create environment **`pypi`** (exactly this name). If GitHub offers required reviewers, configure an owner approval requirement. Avoid allowing unreviewed changes to the release workflow. (The job must use this environment because it is part of the PyPI OIDC publisher identity.)

## 2. Configure PyPI Pending Trusted Publisher

Sign in at https://pypi.org/manage/account/publishing/ and add a **new pending publisher** for a **new project** if the package does not exist yet. Use exactly:

- Project name: `reliable-masked-tabular-imputation`
- PyPI project owner: your own account
- GitHub owner: `lonewolf15116`
- GitHub repository: `reliable-masked-tabular-imputation`
- Workflow filename: `publish-pypi.yml`
- Environment name: `pypi`

If the PyPI project already exists and you control it, configure its Trusted Publisher under that project's **Manage → Publishing** page instead. If another owner already controls the name, **stop** rather than upload under a different identity.

You must complete PyPI login and the Trusted Publisher setup yourself. Neither the repo maintainer nor ChatGPT can infer that setup succeeded merely from an uploaded workflow.

## 3. Run once, manually

In GitHub open **Actions → Publish RMTI v0.1.0 to PyPI → Run workflow**, selecting `main`. If GitHub prompts for environment deployment approval, approve the `pypi` deployment after checking that the workflow is the intended one.

The build stage checks out `v0.1.0`, never the moving `main` head. The publish stage uses OIDC Trusted Publishing and the action `pypa/gh-action-pypi-publish@release/v1`.

## 4. Verify actual PyPI publication

After the workflow reports success, inspect https://pypi.org/project/reliable-masked-tabular-imputation/0.1.0/ and verify wheel and source archive hashes, the MIT licence, version, and provenance. Then, in a fresh environment:

```bash
python -m pip install reliable-masked-tabular-imputation==0.1.0
python -c "from reliable_masked_tabular_imputation import make_mcar_mask, masked_mae; print('RMTI import OK')"
```

**Do not claim the package is published until PyPI confirms it.** Publishing is permanent for a given artifact filename/version; mistakes require a new version.

## Scientific scope

This upload concerns a software utility API (MCAR masking and masked-cell metrics). It does **not** authorise, complete or validate G1B research, MAR mechanisms, dataset provenance, statistical non-inferiority or an imputation estimator.
