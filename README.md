# useenv

A tiny tool to manage values in your env file. 
Useful in some rare circumstances e.g. swapping variables in local development,
when you don't want to maintain multiple separate env files.  

* `pipx install useenv`
* Create a `.useenv.yml` config file in your project root. 
  * If this contains secret values then make sure to add `.useenv.yml` to your project or global `.gitignore`.
* `useenv <env_identifier>`

Example `.useenv.yml` config file:

```yml
env_file: .env
envs:
    foo:
        DATABASE_HOST: foo-host
        DATABASE_USER: foo-user
        DATABASE_PASSWORD: foo-pw
    bar:
        DATABASE_HOST: bar-host
        DATABASE_USER: bar-user
        DATABASE_PASSWORD: bar-pw
```


## Modes

`--mode` flag or `mode` field of the config.

### `merge` (default)

Values will be merged into the existing env file.

### `create`

Env file will be created/overwritten.

In this case you may want to define a common set of values. YAML gives us the tools to do this:

```yml
_common: &common
    DATABASE_USER: common-user
  
env_file: .env
mode: create
envs:
    foo:
        << : *common
        DATABASE_HOST: foo-host    
        DATABASE_PASSWORD: foo-pw
    bar:
        << : *common
        DATABASE_HOST: bar-host    
        DATABASE_PASSWORD: bar-pw
```

## 1password

If you have the 1password CLI installed then you can pull values from 1password:

```yml
...
envs:
    foo:
        DATABASE_PASSWORD: 1pw::<item-id>::<field>  # e.g. 1pw::abcdefqwerty::password
```
