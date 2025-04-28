import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import Top5Careers from './components/CareerList/Top5Careers';
import Bottom3Careers from './components/CareerList/Bottom3Careers';
import UserPrefCareers from './components/CareerList/UserPrefCareers';
import CreateJobForm from './components/CreateJobForm.js'; 
import './App.css';

function App() {
  
  const [recentPosting, setRecentPosting] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const handleCreated = (newId) => {
    // 1. hide the form
    setShowForm(false);

    // 2. re-fetch the list so it includes the newly created job
    fetch('/api/recent-job-postings/')
      .then(r => r.json())
      .then(data => setRecentPosting(data))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetch('/api/recent-job-postings/')
      .then(response => response.json())
      .then(data => {
        setRecentPosting(data);
        console.log('Fetched job postings:', data);
      })
      .catch(error => console.log('Error fetching data:', error));
  }, []);

  return (
    <div className="App">
      <Header />
      <SearchBar />

      {/* ➤ Toggle “New Job” form */}
      <button
        className="new-job-btn"
        onClick={() => setShowForm(f => !f)}
      >
        {showForm ? '✖️ Cancel' : '➕ Create Job Posting'}
      </button>

      {/* ➤ Conditionally render your form */}
      {showForm && <CreateJobForm onSuccess={handleCreated}/>}


      <h1>Recent Job Postings</h1>
      <div className="job-postings-list">
        {recentPosting.length > 0 ? (
          recentPosting.map(post => (
            <div key={post.title} className="job-posting-card">
              <h2>{post.title}</h2>
              <p><strong>Company:</strong> {post.company_name}</p>
            </div>
          ))
        ) : (
          <p>Loading recent job postings...</p>
        )}
      </div>
    </div>
  );
}

export default App;
