module.exports = {
  apps: [
    {
      name: 'vinted-bot-api',
      script: './venv/bin/uvicorn',
      args: 'backend.app.main:app --host 0.0.0.0 --port 8000',
      cwd: '/opt/vinted-bot-saas',
      instances: 1,
      exec_mode: 'fork',  // Changé de 'cluster' à 'fork' pour Python
      env: { 
        PYTHONPATH: '/opt/vinted-bot-saas'
      },
      error_file: '/opt/vinted-bot-saas/logs/api-error.log',
      out_file: '/opt/vinted-bot-saas/logs/api-out.log',
      log_file: '/opt/vinted-bot-saas/logs/api.log'
    },
    {
      name: 'vinted-bot-worker',
      script: './venv/bin/celery',
      args: '-A backend.app.tasks.celery_app worker --loglevel=info --concurrency=2',
      cwd: '/opt/vinted-bot-saas',
      instances: 1,
      exec_mode: 'fork',
      env: { 
        PYTHONPATH: '/opt/vinted-bot-saas'
      },
      error_file: '/opt/vinted-bot-saas/logs/worker-error.log',
      out_file: '/opt/vinted-bot-saas/logs/worker-out.log'
    },
    {
      name: 'vinted-bot-scheduler',
      script: './venv/bin/celery',
      args: '-A backend.app.tasks.celery_app beat --loglevel=info',
      cwd: '/opt/vinted-bot-saas',
      instances: 1,
      exec_mode: 'fork',
      env: { 
        PYTHONPATH: '/opt/vinted-bot-saas'
      },
      error_file: '/opt/vinted-bot-saas/logs/scheduler-error.log',
      out_file: '/opt/vinted-bot-saas/logs/scheduler-out.log'
    }
  ]
};
