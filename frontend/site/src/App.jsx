import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import Home from './pages/Home.jsx';
import Companies from './pages/Companies.jsx';
import Company from './pages/Company.jsx';
import Salary from './pages/Salary.jsx';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/company/:slug" element={<Company />} />
        <Route path="/salary/:uuid" element={<Salary />} />
      </Routes>
    </Layout>
  );
}
