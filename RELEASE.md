# How to Prepare a Release to the `main` Branch

1.  Create a new branch off of `dev` and use the naming scheme `release-<version number>`. If the release to `main` is not iterating a version number, substitute the version number with the current date in `YYYYMMDD` format instead, i.e. `release-<YYYYMMDD>`.

2.  Edit `cookiecutter-templates/cookiecutter-dioptra-deployment/cookiecutter.json` and change any Docker image tags that are set to `latest` to a specific version. The tags should be set to the **latest known working version** for Dioptra. Note, if the repo maintainer in charge of the release has not tested recent releases of third-party images with Dioptra, then they should do so to avoid breakage.

    Check and verify the values set for the following Docker images:

    -   argbash
    -   postgres
    -   dpage/pgadmin4
    -   minio/mc
    -   minio/minio
    -   node
    -   redis

3.  Edit `examples/scripts/venvs/examples-setup-requirements.txt` and set an upper bound constraint on each of the packages listed (if one isn't set already). The upper bounds can be determined by creating the a virtual environment using this file from the `dev` branch and testing that the instructions in `examples/README.md` work. Once the repo maintainer confirms that the environment works and the user can run the provided scripts and submit jobs from the Jupyter notebook, run `python -m pip freeze` to check what is currently installed. Use the known working versions to set the upper bound constraint.

4.  Commit the changes using the message `build: set container tags and package upper bounds for merge to main`

5.  Open a Pull Request on GitHub merging the branch `release-<version number>` (or `release-<YYYYMMDD>`) to the `main` branch. If the update does not bump the version number, give it a title like the following: "Release updates from the dev branch to the main branch - YYYY-MM-DD".

6.  Wait for the GitHub Actions builds and tests to complete. If something fails, diagnose and fix the problem. If everything finishes without error, then prepare to merge. (THIS PART WILL BE DONE VIA THE COMMAND LINE!)

7.  To complete the merge once the tests have run successfully, open a terminal and go to your `dioptra/` folder. Run the following:

    ```sh
    # Fetch the latest changes from origin and remove any deleted branches
    git fetch --prune origin

    # Switch to the main branch (if you aren't on it already)
    git checkout main

    # Update your local repository with the latest changes
    git pull origin main

    # Merge the release branch into main branch (replace <version number> with appropriate text)
    # This will create a merge commit, use the default text for the commit message.
    git merge --no-ff release-<version number>

    # Push the changes
    git push -u origin main

    # Fetch changes from origin and remove any deleted branches
    git fetch --prune origin

    # Remove the merged branch from your local repository (replace <version number> with appropriate text)
    git branch -D release-<version number>
    ```

    Check the Pull Request you opened up on GitHub to verify that it has automatically been closed.
