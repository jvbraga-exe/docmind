import { createRoot } from 'react-dom/client';
import { DocumentsPage } from './features/documents/page';
import './styles.css';

createRoot(document.getElementById('root')!).render(<DocumentsPage />);
