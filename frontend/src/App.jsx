import { useState } from "react";
import axios from "axios";

export default function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const setInputText = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:5000/query", {
        question: input,
      });
      setResponse(res.data);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-center text-white text-xl font-bold bg-blue-600 py-2 mb-4">
        Health Assistant
      </h1>
      <input
        type="text"
        className="bg-gray-100 border p-2 w-full mb-2"
        value={input}
        onChange={setInputText}
        placeholder="Describe your query..."
      />
      <button
        onClick={handleSubmit}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Ask
      </button>

      {loading && <p className="mt-4">Loading...</p>}

      {error && <p className="mt-4 text-red-500">{error}</p>}

      {response && (
        <div className="mt-6 bg-white p-4 border rounded shadow">
          <h2 className="text-lg font-semibold mb-2">Answer:</h2>
          <p>{response.answer} hbbcjahb</p>

          <h3 className="text-md font-semibold mt-4">Context Used:</h3>
          <p className="text-sm text-gray-600">{response.context}</p>
        </div>
      )}
    </div>
  );
}
