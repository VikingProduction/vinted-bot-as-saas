import React from 'react';
import { BrowserRouter, Switch, Route, Redirect } from 'react-router-dom';
import Dashboard from 'layouts/Dashboard';
// importez vos autres pages ici

export default function App() {
  return (
    <BrowserRouter>
      <Switch>
        <Route path="/dashboard" component={Dashboard} />
        {/* Autres routes */}
        <Redirect from="/" to="/dashboard" />
      </Switch>
    </BrowserRouter>
  );
}
