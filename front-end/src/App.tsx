import { Refine } from "@refinedev/core";
import {
    notificationProvider,
    ThemedLayoutV2,
    ThemedHeaderV2,
    ThemedTitleV2,
    ErrorComponent,
    RefineThemes,
} from "@refinedev/antd";
import dataProvider from "../src/utility";
import routerProvider, {
    NavigateToResource,
    UnsavedChangesNotifier,
} from "@refinedev/react-router-v6";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";

import { ConfigProvider } from "antd";
import "@refinedev/antd/dist/reset.css";

import { PermissionDocumentList, PermissionDocumentCreate, PermissionDocumentEdit, PermissionDocumentShow } from "pages/permission-documents";
import { TransactionsList, TransactionShow } from "pages/transactions";

import Signin from './pages/auth/signin.jsx';
import User from './pages/settings/user.jsx';
import Examples from './pages/examples/overview.jsx';
import Example1 from './pages/examples/example1.jsx';
import Example2 from './pages/examples/example2.jsx';
import Example3 from './pages/examples/example3.jsx';
import Example4 from './pages/examples/example4.jsx';


import Authflow from './pages/authflows/authflow2.jsx';
import ActivityFeed from './pages/activity-feed/activity-feed.jsx';
import { DisputeList, DisputeCreate, DisputeEdit, DisputeShow } from "pages/disputes";

// import { WagmiConfig, createConfig, configureChains, sepolia } from 'wagmi'
import { createClient, configureChains, WagmiConfig } from "wagmi";
import { sepolia } from "wagmi/chains";

import { publicProvider } from 'wagmi/providers/public';

const API_URL = "https://api.authe.io";

const { provider, webSocketProvider } = configureChains(
    [sepolia],
    [publicProvider()]
  );
  
  const client = createClient({
    provider,
    webSocketProvider,
    autoConnect: true,
  });

// const { chains, publicClient, webSocketPublicClient } = configureChains(
//     [sepolia],
//     [publicProvider()],
//   )
   
//   const config = createConfig({
//     autoConnect: true,
//     publicClient,
//     webSocketPublicClient,
//   })

const App: React.FC = () => {
    return (
        <WagmiConfig client={client}>
        {/* <WagmiConfig config={config}> */}
        <BrowserRouter>
            <ConfigProvider theme={RefineThemes.Blue}>
                <Refine
                    dataProvider={dataProvider(API_URL)}
                    routerProvider={routerProvider}
                    resources={[
                        {
                            name: "permission-documents",
                            list: "/permission-documents",
                            create: "/permission-documents/create",
                            edit: "/permission-documents/edit/:id",
                            show: "/permission-documents/show/:id",
                        },
                        {
                            name: "transactions",
                            list: "/transactions",
                            show: "/transactions/show/:id",
                        },
                        // {
                        //     name: "tasks",
                        //     list: "/tasks",
                        //     create: "/tasks/create",
                        //     edit: "/tasks/edit/:id",
                        //     show: "/tasks/show/:id",
                        // },
                        // {
                        //     name: "notifications",
                        //     list: "/notifications",
                        //     create: "/notifications/create",
                        //     edit: "/notifications/edit/:id",
                        //     show: "/notifications/show/:id",
                        // },
                        {
                            name: "disputes",
                            list: "/disputes",
                            create: "/disputes/create",
                            edit: "/disputes/edit/:id",
                            show: "/disputes/show/:id",
                        },
                        {
                            name: "settings",
                            list: "/settings",
                        },
                        {
                            name: "activity-feed",
                            list: "/activity-feed",
                        },
                        {
                            name: "authflow",
                            list: "/authflow",
                        },
                        {
                            name: "examples",
                            list: "/examples",
                            show: "/examples/show/example1",
                        },

                        // {
                        //     name: "categories",
                        //     list: "/categories",
                        //     create: "/categories/create",
                        //     edit: "/categories/edit/:id",
                        // },
                    ]}
                    notificationProvider={notificationProvider}
                    options={{
                        syncWithLocation: true,
                        warnWhenUnsavedChanges: true,
                    }}
                >
                    <Routes>
                        <Route
                            element={
                                <ThemedLayoutV2 Header={() => <ThemedHeaderV2 sticky />}
                                Title={({ collapsed }) => (
                                    <ThemedTitleV2
                                        // collapsed is a boolean value that indicates whether the <Sidebar> is collapsed or not
                                        collapsed={collapsed}
                                        text="Authe"
                                    />
                                )}
                                
                                >
                                    <Outlet />
                                </ThemedLayoutV2>
                            }
                        >
                            <Route
                                index
                                element={
                                    <NavigateToResource resource="permission-documents" />
                                }
                            />
                            <Route path="/permission-documents">
                                <Route index element={<PermissionDocumentList />} />
                                <Route path="create" element={<PermissionDocumentCreate />} />
                                <Route path="edit/:id" element={<PermissionDocumentEdit />} />
                                <Route path="show/:id" element={<PermissionDocumentShow />} /> 
                            </Route>
                            <Route path="/transactions">
                                <Route index element={<TransactionsList />} />
                                <Route path="show/:id" element={<TransactionShow />} /> 
                            </Route>
                            <Route path="/tasks">
                                <Route index element={<PermissionDocumentList />} />
                                <Route path="create" element={<PermissionDocumentCreate />} />
                                <Route path="edit/:id" element={<PermissionDocumentEdit />} />
                                <Route path="show/:id" element={<PermissionDocumentShow />} /> 
                            </Route>
                            <Route path="/disputes">
                                <Route index element={<DisputeList />} />
                                <Route path="create" element={<DisputeCreate />} />
                                <Route path="edit/:id" element={<DisputeEdit />} />
                                <Route path="show/:id" element={<DisputeShow />} /> 
                            </Route>
                            {/* <Route path="/categories">
                                <Route index element={<CategoryList />} />
                                <Route
                                    path="create"
                                    element={<CategoryCreate />}
                                />
                                <Route
                                    path="edit/:id"
                                    element={<CategoryEdit />}
                                />
                            </Route> */}
                            <Route path='/authflow' element={<Authflow />} />
                            <Route path='/settings' element={<User /> } /> 
                            <Route path='/activity-feed' element={<ActivityFeed /> } /> 
                            <Route path='/examples'> 
                                <Route index element={<Examples />} />
                                <Route path="show/example1" element={<Example1 />} /> 
                                <Route path="show/example2" element={<Example2 />} /> 
                                <Route path="show/example3" element={<Example3 />} /> 
                                <Route path="show/example4" element={<Example4 />} /> 
                            </Route>

                            <Route path='/signin' element={<Signin />} />
                            <Route path="*" element={<ErrorComponent  />} />
                        </Route>
                    </Routes>
                    <UnsavedChangesNotifier />
                </Refine>
            </ConfigProvider>
        </BrowserRouter>
        </WagmiConfig>
    );
};

export default App;
