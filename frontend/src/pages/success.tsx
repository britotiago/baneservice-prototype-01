import React from 'react';
import { useRouter } from 'next/router';

const Success = () => {
    const router = useRouter();
    const { fileUrl } = router.query;  // Retrieve the fileUrl from the query parameters

    return (
        <div className="flex flex-col items-center justify-center min-h-screen">
            <h1 className="text-2xl font-bold mb-4">Submission Sent Successfully</h1>
            {fileUrl ? (
                <a href={fileUrl as string} download className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer">
                    Download Document
                </a>
            ) : (
                <p>No file available for download.</p>
            )}
            <button
                onClick={() => router.push('/')} // Navigates back to the homepage
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer mt-4"
            >
                Submit Another Project
            </button>
        </div>
    );
};

export default Success;
