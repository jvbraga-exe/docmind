# Front-end do DocMind

Instale as dependências com `npm install` nesta pasta. Na pasta principal do projeto, rode `npm run dev` no Windows ou `npm run dev:unix` no Linux/macOS. O `concurrently` inicia o Vite e a API Python juntos. Abra `http://127.0.0.1:5173`.

O Vite encaminha as chamadas `/api` para `http://127.0.0.1:8084`.

`npm run build` gera os arquivos de produção em `dist/`. O front-end pode ser hospedado separado do backend; configure `VITE_API_BASE_URL` com o endereço da API e `CORS_ORIGINS` no backend com o endereço do front-end.
