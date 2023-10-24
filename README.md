# useenv

A tiny tool to update your env file.

* Clone the repo.
* `pipx install <path to repo>`
* Create a `.useenv` config file in your project root. 
  If this contains secret values then make sure to add `.useenv` to your project or global `.gitignore`.
* `useenv <env_identifier>`.

Example `.useenv` config file:

```
env_file: .env
envs:
    foo:
        DATABASE_HOST: "..."
        DATABASE_NAME: "..."
        DATABASE_USER: "..."
        DATABASE_PASSWORD: "..."
    bar:
        DATABASE_HOST: "..."
        DATABASE_NAME: "..."
        DATABASE_USER: "..."
        DATABASE_PASSWORD: "..."
```
