@echo off
echo ========================================
echo SearXNG-SGA Git 设置和推送脚本
echo ========================================

echo 1. 初始化Git仓库...
git init

echo 2. 添加所有文件到暂存区...
git add .

echo 3. 创建.gitignore文件...
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo pip-wheel-metadata/
echo share/python-wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo MANIFEST
echo.
echo # PyInstaller
echo *.manifest
echo *.spec
echo.
echo # Installer logs
echo pip-log.txt
echo pip-delete-this-directory.txt
echo.
echo # Unit test / coverage reports
echo htmlcov/
echo .tox/
echo .nox/
echo .coverage
echo .coverage.*
echo .cache
echo nosetests.xml
echo coverage.xml
echo *.cover
echo *.py,cover
echo .hypothesis/
echo .pytest_cache/
echo.
echo # Translations
echo *.mo
echo *.pot
echo.
echo # Django stuff:
echo *.log
echo local_settings.py
echo db.sqlite3
echo db.sqlite3-journal
echo.
echo # Flask stuff:
echo instance/
echo .webassets-cache
echo.
echo # Scrapy stuff:
echo .scrapy
echo.
echo # Sphinx documentation
echo docs/_build/
echo.
echo # PyBuilder
echo target/
echo.
echo # Jupyter Notebook
echo .ipynb_checkpoints
echo.
echo # IPython
echo profile_default/
echo ipython_config.py
echo.
echo # pyenv
echo .python-version
echo.
echo # pipenv
echo Pipfile.lock
echo.
echo # PEP 582
echo __pypackages__/
echo.
echo # Celery stuff
echo celerybeat-schedule
echo celerybeat.pid
echo.
echo # SageMath parsed files
echo *.sage.py
echo.
echo # Environments
echo .env
echo .venv
echo env/
echo venv/
echo ENV/
echo env.bak/
echo venv.bak/
echo.
echo # Spyder project settings
echo .spyderproject
echo .spyproject
echo.
echo # Rope project settings
echo .ropeproject
echo.
echo # mkdocs documentation
echo /site
echo.
echo # mypy
echo .mypy_cache/
echo .dmypy.json
echo dmypy.json
echo.
echo # Pyre type checker
echo .pyre/
echo.
echo # SearXNG specific
echo searx/settings.yml
echo searx/settings_local.yml
echo.
echo # Docker
echo .dockerignore
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Logs
echo *.log
echo logs/
echo.
echo # Temporary files
echo *.tmp
echo *.temp
echo.
echo # Redis
echo dump.rdb
echo.
echo # Node.js
echo node_modules/
echo npm-debug.log*
echo yarn-debug.log*
echo yarn-error.log*
echo.
echo # Static files
echo /static/
echo /media/
echo.
echo # Backup files
echo *.bak
echo *.backup
echo.
echo # Local configuration
echo config.local.yml
echo settings.local.yml
echo.
echo # Test files
echo test_*.py
echo *_test.py
echo tests/
echo.
echo # Coverage reports
echo htmlcov/
echo .coverage
echo coverage.xml
echo.
echo # Profiling
echo *.prof
echo.
echo # Database
echo *.db
echo *.sqlite
echo *.sqlite3
echo.
echo # Cache
echo .cache/
echo cache/
echo.
echo # Temporary directories
echo tmp/
echo temp/
echo.
echo # Lock files
echo *.lock
echo.
echo # Package files
echo *.tar.gz
echo *.zip
echo *.rar
echo.
echo # Configuration backups
echo *.conf.bak
echo *.yaml.bak
echo *.yml.bak
echo.
echo # Docker volumes
echo docker-data/
echo.
echo # Local development
echo .local/
echo local/
echo.
echo # Editor backups
echo *~
echo .*.swp
echo .*.swo
echo.
echo # OS generated files
echo .DS_Store
echo .DS_Store?
echo ._*
echo .Spotlight-V100
echo .Trashes
echo ehthumbs.db
echo Thumbs.db
echo.
echo # Windows
echo desktop.ini
echo.
echo # Linux
echo *~
echo.
echo # macOS
echo .AppleDouble
echo .LSOverride
echo.
echo # Icon must end with two \r
echo Icon
echo.
echo # Thumbnails
echo ._*
echo.
echo # Files that might appear in the root of a volume
echo .DocumentRevisions-V100
echo .fseventsd
echo .Spotlight-V100
echo .TemporaryItems
echo .Trashes
echo .VolumeIcon.icns
echo .com.apple.timemachine.donotpresent
echo.
echo # Directories potentially created on remote AFP share
echo .AppleDB
echo .AppleDesktop
echo Network Trash Folder
echo Temporary Items
echo .apdisk > .gitignore

echo 4. 提交初始版本...
git commit -m "feat: 初始化SearXNG-SGA项目

- 添加Dify集成支持
- 添加微信专搜API
- 完整的Windows兼容性支持
- Docker部署支持
- 详细的文档和使用指南"

echo.
echo ========================================
echo Git仓库已初始化并创建了初始提交！
echo.
echo 下一步操作：
echo 1. 在GitHub上创建新仓库
echo 2. 复制仓库URL
echo 3. 运行以下命令连接远程仓库：
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 或者如果已有仓库，运行：
echo    git remote add origin YOUR_REPO_URL
echo    git push -u origin main
echo ========================================
pause 