import React, { useState, useEffect } from 'react';

interface AuditCriteria {
    criteria_id: string;
    name: string;
    description: string;
    type: string | null;
    issue_number: string;
    issue_name: string;
    category_number: string;
    category_name: string;
}

interface AuditCriteriaDropdownProps {
    onChange: (criteria: AuditCriteria) => void;
}

const AuditCriteriaDropdown: React.FC<AuditCriteriaDropdownProps> = ({ onChange }) => {
    const [criteria, setCriteria] = useState<AuditCriteria[]>([]);
    const [inputValue, setInputValue] = useState<string>('');
    const [filteredCriteria, setFilteredCriteria] = useState<AuditCriteria[]>([]);
    const [dropdownVisible, setDropdownVisible] = useState<boolean>(false);

    useEffect(() => {
        const fetchCriteria = async () => {
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/criteria`);
                if (!response.ok) {
                    throw new Error('Nettverksresponsen var ikke ok ' + response.statusText);
                }
                const data: AuditCriteria[] = await response.json();
                setCriteria(data);
                setFilteredCriteria(data);
            } catch (error) {
                console.error('Kunne ikke hente kriterier:', error);
            }
        };
        fetchCriteria();
    }, []);

    useEffect(() => {
        if (inputValue) {
            const filtered = criteria.filter(crit =>
                crit.criteria_id.toLowerCase().includes(inputValue.toLowerCase())
            );
            setFilteredCriteria(filtered);
            setDropdownVisible(true);
        } else {
            setFilteredCriteria(criteria);
            setDropdownVisible(false);
        }
    }, [inputValue, criteria]);

    const handleSelect = (crit: AuditCriteria) => {
        onChange(crit); // Propagate the change to the parent form
        setInputValue(crit.criteria_id);
        setDropdownVisible(false); // Hide the dropdown immediately after selection
    };

    return (
        <div>
            <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onFocus={() => setDropdownVisible(true)}
                onBlur={() => setTimeout(() => setDropdownVisible(false), 200)} // Delay hiding to allow selection
                className="mt-1 block w-full p-2 border border-gray-300 rounded-md"
                placeholder="Legg inn Revisjonskriteria"
            />
            {dropdownVisible && (
                <ul className="max-h-60 overflow-auto border border-gray-300 rounded-md">
                    {filteredCriteria.map((crit) => (
                        <li
                            key={crit.criteria_id}
                            onClick={() => handleSelect(crit)}
                            className="p-2 hover:bg-gray-100 cursor-pointer"
                        >
                            {crit.criteria_id}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default AuditCriteriaDropdown;
