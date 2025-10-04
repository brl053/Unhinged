import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ReactDOM from "react-dom/client";
import App from "./App";
import { createAppRouter } from "./routing/routes";
import { initializeDatabase } from "./services/db";

interface IMountArgs {
    mountPoint: HTMLElement
    mountOptions?: Record<string, unknown>
}

const mount = ({ mountPoint, mountOptions }: IMountArgs): (() => void) => {
    const router = createAppRouter();
    const queryClient = new QueryClient();

    // Initialize IndexedDB
    initializeDatabase().catch(error => {
        console.error('Failed to initialize database:', error);
    });

    const root = ReactDOM.createRoot(mountPoint);
    root.render(
        <QueryClientProvider client={queryClient}>
            <App router={router}/>
        </QueryClientProvider>
    );

    return () => queueMicrotask(() => root.unmount());
}

export { mount}