import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Dashboard from './Dashboard';

function App() {
  return (
    <div className="App">
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
        <div className="container-fluid">
          <a className="navbar-brand" href="/">Ofipensiones</a>
        </div>
      </nav>

      <div className="container mt-4">
        <Dashboard />
      </div>
    </div>
  );
}

export default App;
