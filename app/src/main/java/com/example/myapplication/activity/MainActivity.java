package com.example.myapplication.activity;

import android.content.Intent;
import android.database.sqlite.SQLiteException;
import android.os.Bundle;
import android.widget.Toast;

import com.example.myapplication.R;
import com.example.myapplication.adapter.AppointmentAdapter;
import com.example.myapplication.database.DatabaseHelper;
import com.example.myapplication.databinding.ActivityMainBinding;

import java.util.ArrayList;

public class MainActivity extends AppointmentActivity {
    public static final String EXTRA_APPOINTMENT_ID = "appointment_id";
    private ActivityMainBinding binding;
    private DatabaseHelper database;
    private AppointmentAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setScreen(binding.getRoot());
        database = new DatabaseHelper(this);
        adapter = new AppointmentAdapter(this, new ArrayList<>());
        binding.lvAppointments.setAdapter(adapter);
        binding.lvAppointments.setEmptyView(binding.tvEmpty);
        binding.btnAdd.setOnClickListener(view ->
                startActivity(new Intent(this, AddAppointmentActivity.class)));
        binding.lvAppointments.setOnItemClickListener((parent, view, position, id) -> {
            Intent intent = new Intent(this, AppointmentDetailActivity.class);
            intent.putExtra(EXTRA_APPOINTMENT_ID, adapter.getItem(position).getId());
            startActivity(intent);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        try {
            adapter.updateData(database.getAllAppointments());
            binding.tvStats.setText(getString(R.string.stats_format,
                    database.countAll(), database.countReminders()));
        } catch (SQLiteException exception) {
            Toast.makeText(this, R.string.database_error, Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onDestroy() {
        database.close();
        super.onDestroy();
    }
}
