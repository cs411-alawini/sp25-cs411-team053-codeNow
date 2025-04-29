// src/App.js
import React, { useEffect, useState } from 'react';
import { Routes, Route }            from 'react-router-dom';
import Home                         from './components/Home';
import JobDetail                    from './components/JobDetail';
import CompanyJobs                  from './components/CompanyJobs';
import './App.css';

function App() {
  const [recentPosting, setRecentPosting]     = useState([]);
  const [searchResults, setSearchResults]     = useState(null);  // <— null = no search yet
  const [showForm, setShowForm]               = useState(false);

  // fetch recent on mount & after create
  const fetchRecent = () => {
    fetch('/api/recent-job-postings/')
      .then(r => r.json())
      .then(setRecentPosting)
      .catch(console.error);
  };
  useEffect(fetchRecent, []);

  const handleCreated = () => {
    setShowForm(false);
    fetchRecent();
  };

  // ← new search handler:
  const handleSearch = term => {
    if (!term) {
      setSearchResults(null);   // clear search, go back to recents
      return;
    }
    fetch(`/api/search_jobs/?keyword=${encodeURIComponent(term)}`)
      .then(r => {
        if (!r.ok) throw new Error(r.statusText);
        return r.json();
      })
      .then(results => setSearchResults(results))
      .catch(err => {
        console.error(err);
        setSearchResults([]); // no matches or error
      });
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Home
            recentPosting={recentPosting}
            searchResults={searchResults}
            onSearch={handleSearch}       // pass search handler
            showForm={showForm}
            setShowForm={setShowForm}
            onCreated={handleCreated}
          />
        }
      />
      <Route path="/job/:id" element={<JobDetail />} />
      <Route path="/company/:companyId" element={<CompanyJobs />} />
    </Routes>
  );
}

export default App;
