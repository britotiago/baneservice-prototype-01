import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';

const Processing = () => {
    const router = useRouter();
    const { taskId } = router.query;  // Retrieve taskId from the query

    const [loading, setLoading] = useState(true);
    const [fileUrl, setFileUrl] = useState('');

    useEffect(() => {
        if (taskId) {
            // Start polling the backend for task status
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`http://127.0.0.1:8000/api/task-status/${taskId}`);
                    const result = await response.json();
                    if (result.status === 'completed') {
                        setFileUrl(result.file_url);
                        setLoading(false);
                    }
                } catch (error) {
                    console.error('Feil ved henting av oppgavestatus:', error);
                }
            }, 5000);  // Poll every 5 seconds

            return () => clearInterval(interval);  // Cleanup on component unmount
        }
    }, [taskId]);

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            {loading ? (
                <div className="flex flex-col items-center">
                    {/* Tailwind CSS spinner */}
                    <div className="animate-spin rounded-full h-32 w-32 border-t-4 border-blue-500 border-solid border-r-transparent"></div>
                    <p className="text-xl font-semibold mt-6 text-gray-700">Behandler... Vennligst vent.</p>
                </div>
            ) : (
                <div className="text-center">
                    <h1 className="text-2xl font-bold mb-4">Dokumentet er klart</h1>
                    <a
                        href={fileUrl}
                        download
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    >
                        Last ned dokumentet
                    </a>
                    <button
                        onClick={() => router.push('/')}
                        className="mt-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
                    >
                        Send inn et nytt prosjekt
                    </button>
                </div>
            )}
        </div>
    );
};

export default Processing;
