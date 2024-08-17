// app/page.tsx
"use client";

import * as React from "react";
import { useEffect, useState, useRef } from "react";
import { DataGrid, GridColDef, GridActionsCellItem } from "@mui/x-data-grid";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import CancelIcon from "@mui/icons-material/Cancel";
// Removed the import for DeleteIcon due to the error

interface InventoryItem {
  id: number;
  name: string;
  quantity: number;
  expiration_date: string;
}

const Home: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [recording, setRecording] = useState<boolean>(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<string | null>(null);
  const [editRowsModel, setEditRowsModel] = useState<any>({});

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    async function fetchInventory() {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/`
      );
      const data = await res.json();
      setInventory(data);
    }

    fetchInventory();
  }, []);

  const handleDelete = async (id: number) => {
    await fetch(`${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/${id}/`, {
      method: "DELETE",
    });
    setInventory((prev) => prev.filter((item) => item.id !== id));
  };

  const handleEdit = async (
    id: number,
    field: keyof InventoryItem,
    value: any
  ) => {
    const updatedItem = inventory.find((item) => item.id === id);
    if (updatedItem) {
      (updatedItem[field] as any) = value;
      await fetch(`${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/${id}/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedItem),
      });
      setInventory((prev) =>
        prev.map((item) => (item.id === id ? updatedItem : item))
      );
    }
  };

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      streamRef.current = stream;
      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };
      mediaRecorderRef.current.onstop = handleStop;
      mediaRecorderRef.current.start();
      setRecording(true);
    });
  };

  const stopRecording = () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      mediaRecorderRef.current.stop();
    }
    setRecording(false);

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  };

  const handleStop = () => {
    const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(audioBlob);
    setAudioURL(audioUrl);
    audioChunks.current = [];

    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");

    fetch(
      `${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/transcribe_and_process/`,
      {
        method: "POST",
        body: formData,
      }
    )
      .then((res) => res.json())
      .then((data) => {
        if (data.task_id) {
          setTaskId(data.task_id);
          checkTaskStatus(data.task_id);
        }
      });
  };

  const checkTaskStatus = (taskId: string) => {
    fetch(
      `${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/task_status/?task_id=${taskId}`
    )
      .then((res) => res.json())
      .then((data) => {
        setTaskStatus(data.status);
        if (data.status !== "SUCCESS" && data.status !== "FAILURE") {
          setTimeout(() => checkTaskStatus(taskId), 2000);
        }
      })
      .then(async () => {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_HOST_URL}/api/inventory/`
        );
        const data = await res.json();
        setInventory(data);
      })
  };


  const handleProcessRowUpdate = (newRow: any, oldRow: any) => {
    const updatedRow = { ...newRow };
    handleEdit(updatedRow.id, "name", updatedRow.name);
    handleEdit(updatedRow.id, "quantity", updatedRow.quantity);
    handleEdit(updatedRow.id, "expiration_date", updatedRow.expiration_date);
    return updatedRow;
  };

  const columns: GridColDef[] = [
    { field: "id", headerName: "ID", width: 90 },
    { field: "name", headerName: "Name", width: 150, editable: true },
    { field: "quantity", headerName: "Quantity", width: 150, editable: true },
    {
      field: "expiration_date",
      headerName: "Expiration Date",
      width: 180,
      editable: true,
    },
    {
      field: "actions",
      headerName: "Actions",
      type: "actions",
      width: 100,
      getActions: (params) => [
        <GridActionsCellItem
          key={params.id}
          icon={<DeleteIcon />}
          label="Delete"
          onClick={() => handleDelete(params.id as number)}
        />,
      ],
    },
  ];

  return (
    <div className="dark:bg-gray-900 dark:text-white min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Inventory and Recording</h1>

      <section className="mb-8">
        <h2 className="text-xl mb-2">Inventory</h2>
        <div style={{ height: 400, width: "100%" }}>
          <DataGrid
            rows={inventory}
            columns={columns}
            pageSizeOptions={[5]} // Changed from rowsPerPageOptions
            disableRowSelectionOnClick // Updated property name
            editMode="row"
            processRowUpdate={handleProcessRowUpdate}
            sx={{
              backgroundColor: "background.paper",
              "& .MuiDataGrid-cell": {
                color: "text.primary",
              },
              "& .MuiDataGrid-columnsContainer, .MuiDataGrid-footerContainer": {
                backgroundColor: "background.default",
              },
              "& .MuiDataGrid-row": {
                backgroundColor: "background.paper",
              },
              "& .MuiDataGrid-columnHeaderTitle": {
                color: "text.secondary",
              },
            }}
          />
        </div>
      </section>

      <section>
        <h2>Record Audio</h2>
        <button onClick={recording ? stopRecording : startRecording}>
          {recording ? "Stop Recording" : "Start Recording"}
        </button>
        {audioURL && <audio src={audioURL} controls />}
        {taskId && <p>Task ID: {taskId}</p>}
        {taskStatus && <p>Task Status: {taskStatus}</p>}
      </section>
    </div>
  );
};

export default Home;