import React, { useState, ChangeEvent, FormEvent } from 'react';
import { useRouter } from 'next/router';
import FileUpload from './FileUpload';
import AuditCriteriaDropdown from './AuditCriteriaDropdown';

interface FormData {
    projectName: string;
    breeamEntrepreneurResponsible: string;
    breeamCivilEngineerResponsible: string;
    breeamAssessor: string;
    auditCriteria: string;
    premise: string;
    preparedBy: string;
}

const ProjectForm = () => {
    const router = useRouter();
    const [formData, setFormData] = useState<FormData>({
        projectName: '',
        breeamEntrepreneurResponsible: '',
        breeamCivilEngineerResponsible: '',
        breeamAssessor: '',
        auditCriteria: '',
        premise: '',
        preparedBy: ''
    });
    const [files, setFiles] = useState<File[]>([]);
    const [loading, setLoading] = useState(false);  // State to manage loading

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);  // Start loading
        console.log("Form submission started.");

        const submissionData = new FormData();
        submissionData.append('data', JSON.stringify(formData));
        files.forEach(file => submissionData.append('file', file));

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/upload/`, {
                method: 'POST',
                body: submissionData
            });

            console.log("Response received:", response);

            const result = await response.json();
            console.log("Result parsed:", result);

            if (response.ok) {
                // Navigate to the processing page with a taskId or other identifier
                console.log("Redirecting to processing page with taskId:", result.taskId);
                router.push(`/processing?taskId=${result.taskId}`);
            } else {
                console.error('Feil:', result.message);
            }
        } catch (error) {
            console.error('Feil:', error);
        } finally {
            setLoading(false);  // Stop loading
            console.log("Loading state set to false.");
        }
    };

    return (
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {loading ? (
                <div className="flex flex-col items-center">
                    {/* Tailwind CSS spinner */}
                    <div
                        className="animate-spin rounded-full h-32 w-32 border-t-4 border-blue-500 border-solid border-r-transparent"></div>
                    <p className="text-xl font-semibold mt-6 text-gray-700">Behandler... Vennligst vent.</p>
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6 py-6">
                    {Object.keys(formData).map((key) => (
                        key === 'premise' ? (
                            <div key={key} className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 capitalize">
                                    Premiss
                                </label>
                                <select
                                    name={key}
                                    value={formData[key as keyof FormData]}
                                    onChange={handleChange}
                                    className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                    required
                                >
                                    <option value="">Velg Ja eller Nei</option>
                                    <option value="ja">Ja</option>
                                    <option value="nei">Nei</option>
                                </select>
                            </div>
                        ) : key !== 'auditCriteria' && (
                            <div key={key} className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 capitalize">
                                    {key === 'projectName' ? 'Prosjekt' :
                                        key === 'breeamEntrepreneurResponsible' ? 'BREEAM Inf. ansvarlig hos entreprenør' :
                                            key === 'breeamCivilEngineerResponsible' ? 'BREEAM Inf. ansvarlig hos byggherre' :
                                                key === 'breeamAssessor' ? 'BREEAM Assessor' :
                                                    key === 'preparedBy' ? 'Utarbeidet av' : key.replace(/([A-Z])/g, ' $1')}
                                </label>
                                <input
                                    type="text"
                                    name={key}
                                    value={formData[key as keyof FormData]}
                                    onChange={handleChange}
                                    className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                                    required
                                />
                            </div>
                        )
                    ))}
                    <div className="mb-4 md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700">Revisjonskriteria</label>
                        <AuditCriteriaDropdown onChange={(criteria) => setFormData({...formData, auditCriteria: criteria.criteria_id})} />
                    </div>
                    <div className="md:col-span-2">
                        <FileUpload files={files} setFiles={setFiles} />
                    </div>
                    <div className="md:col-span-2">
                        <button
                            type="submit"
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded w-full md:w-auto"
                        >
                            Send inn
                        </button>
                    </div>
                </form>
            )}
        </div>
    );
};

export default ProjectForm;
