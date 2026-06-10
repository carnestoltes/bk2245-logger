## Instalation

If the device has git and docker, follow the steps bellow to upload and charge the service:

```bash
cd /home/$USER/bk2245-logger
```

### Download the new branch metadata from GitHub

```bash
git fetch origin
```
### Switch over to your new docker branch natively

```bash
git checkout feature/dockerization
```
### Run the system

```bash
docker compose up -d --build
```
