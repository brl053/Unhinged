import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ReactDOM from "react-dom/client";
import App from "./App";
import { createBrowserRouter } from "react-router-dom";
import { routes } from "./routing/routes";

interface IMountArgs {
    mountPoint: HTMLElement
    mountOptions?: Record<string, unknown>
}

const mount = ({ mountPoint, mountOptions }: IMountArgs): (() => void) => {
    const basename = mountOptions?.basename as string
    const router = basename === undefined
            ? createBrowserRouter(Object.values(routes))
            : createBrowserRouter(Object.values(routes), { basename });
    const queryClient = new QueryClient();

    const root = ReactDOM.createRoot(mountPoint);
    root.render(
        <QueryClientProvider client={queryClient}>
            <App router={router}/>
        </QueryClientProvider>
    );

    return () => queueMicrotask(() => root.unmount());
}

export { mount}