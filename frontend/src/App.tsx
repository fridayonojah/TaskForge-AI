import { AuthProvider, useAuth } from "./hooks/useAuth";

import { AppLayout } from "./components/layout/AppLayout";
import { AuthPage } from "./components/auth/AuthPage";

function Root() {
  const { token } = useAuth();
  return token ? <AppLayout /> : <AuthPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <Root />
    </AuthProvider>
  );
}
