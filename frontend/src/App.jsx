import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import NavLink from './components/NavLink';
import FileUpload from './components/FileUpload';
import DatasetCard from './components/DatasetCard';
import AnalysisView from './components/AnalysisView';
import ChatInterface from './components/ChatInterface';

export default function App() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [chatDataset, setChatDataset] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  /* ---------------- Handlers ---------------- */

  // 1. Upload Handler with Polling
  const handleUpload = async (file) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/upload', {
        method: 'POST',
        body: formData,
      });
      const initialData = await response.json();
      
      // Add to state immediately with 'analyzing' status
      setDatasets((prev) => [initialData, ...prev]);

      // Start Polling for the result
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`http://localhost:8000/api/v1/dataset/${initialData.id}`);
          const updatedData = await statusRes.json();

          if (updatedData.analysis_status === 'completed') {
            setDatasets((prev) => 
              prev.map(d => d.id === initialData.id ? updatedData : d)
            );
            clearInterval(pollInterval);
          } else if (updatedData.analysis_status === 'failed') {
            clearInterval(pollInterval);
            alert("Analysis failed for " + file.name);
          }
        } catch (pollError) {
          console.error("Polling error:", pollError);
        }
      }, 3000); 

    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload file. Check if backend is running.");
    } finally {
      setIsUploading(false);
    }
  };

  // 2. The Missing Delete Handler (Restored)
  const handleDelete = (id) => {
    setDatasets((prev) => prev.filter((d) => d.id !== id));
    if (selectedDataset?.id === id) setSelectedDataset(null);
    if (chatDataset?.id === id) setChatDataset(null);
  };

  /* ---------------- Layout ---------------- */
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <div className="flex flex-1">
          <NavLink />
          <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
            <Routes>
              <Route path="/" element={
                  <>
                    {!selectedDataset && !chatDataset && (
                      <>
                        <FileUpload onUpload={handleUpload} isUploading={isUploading} />
                        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                          {datasets.map((dataset) => (
                            <DatasetCard
                              key={dataset.id}
                              dataset={dataset}
                              onDelete={handleDelete} // FIXED: handleDelete is now defined
                              onSelect={setSelectedDataset}
                              onChat={setChatDataset}
                            />
                          ))}
                        </div>
                      </>
                    )}

                    {selectedDataset && (
                      <AnalysisView
                        dataset={selectedDataset}
                        onBack={() => setSelectedDataset(null)}
                        onChat={() => {
                          setChatDataset(selectedDataset);
                          setSelectedDataset(null);
                        }}
                      />
                    )}

                    {chatDataset && (
                      <ChatInterface
                        dataset={chatDataset}
                        onBack={() => setChatDataset(null)}
                      />
                    )}
                  </>
                }
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}