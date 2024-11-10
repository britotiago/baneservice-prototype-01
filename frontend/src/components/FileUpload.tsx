import React, { ChangeEvent } from 'react';

interface FileUploadProps {
    files: File[];
    setFiles: React.Dispatch<React.SetStateAction<File[]>>;
}

const FileUpload: React.FC<FileUploadProps> = ({ files, setFiles }) => {
    const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFiles([...files, ...Array.from(event.target.files)]);
        }
    };

    const handleRemoveFile = (index: number) => {
        // Remove file from the files array at the specific index
        const newFiles = files.filter((_, idx) => idx !== index);
        setFiles(newFiles);
    };

    return (
        <div>
            <label className="block text-sm font-medium text-gray-700">Last opp dokumentasjonsfiler</label>
            <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
            />
            <div className="mt-2">
                {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        {file.name}
                        <button onClick={() => handleRemoveFile(index)} className="text-red-500 hover:text-red-700">
                            Fjern
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FileUpload;
