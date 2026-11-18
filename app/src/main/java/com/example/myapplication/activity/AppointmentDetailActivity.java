package com.example.myapplication.activity;

import android.database.sqlite.SQLiteException;
import android.os.Bundle;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;

import com.example.myapplication.R;
import com.example.myapplication.database.DatabaseHelper;
import com.example.myapplication.databinding.ActivityAppointmentDetailBinding;
import com.example.myapplication.model.Appointment;
import com.example.myapplication.util.AppointmentDateTime;

public class AppointmentDetailActivity extends AppointmentActivity {
    private ActivityAppointmentDetailBinding binding;
    private DatabaseHelper database;
    private Appointment appointment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityAppointmentDetailBinding.inflate(getLayoutInflater());
        setScreen(binding.getRoot());
        database = new DatabaseHelper(this);
        binding.btnBack.setOnClickListener(view -> finish());
        binding.btnDelete.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle(R.string.delete_title)
                .setMessage(getString(R.string.delete_message, appointment.getTitle()))
                .setNegativeButton(R.string.cancel, null)
                .setPositiveButton(R.string.delete, (dialog, which) -> delete())
                .show());
    }

    @Override
    protected void onResume() {
        super.onResume();
        try {
            int id = getIntent().getIntExtra(MainActivity.EXTRA_APPOINTMENT_ID, -1);
            appointment = database.getAppointmentById(id);
            if (appointment == null) {
                Toast.makeText(this, R.string.appointment_missing, Toast.LENGTH_SHORT).show();
                finish();
                return;
            }
            binding.tvTitle.setText(appointment.getTitle());
            binding.tvLocation.setText(appointment.getLocation());
            binding.tvDateTime.setText(AppointmentDateTime.format(appointment.getDate(), appointment.getTime()));
            binding.swReminder.setOnCheckedChangeListener(null);
            binding.swReminder.setChecked(appointment.isReminder());
            updateReminderStatus();
            binding.swReminder.setOnCheckedChangeListener((button, checked) -> {
                if (checked == appointment.isReminder()) {
                    return;
                }
                try {
                    database.updateReminder(appointment.getId(), checked);
                    appointment.setReminder(checked);
                    updateReminderStatus();
                } catch (SQLiteException exception) {
                    button.setChecked(appointment.isReminder());
                    Toast.makeText(this, R.string.database_error, Toast.LENGTH_LONG).show();
                }
            });
        } catch (SQLiteException exception) {
            Toast.makeText(this, R.string.database_error, Toast.LENGTH_LONG).show();
            finish();
        }
    }

    private void updateReminderStatus() {
        binding.tvReminderStatus.setText(appointment.isReminder()
                ? R.string.reminder_on : R.string.reminder_off);
    }

    private void delete() {
        try {
            database.deleteAppointment(appointment.getId());
            Toast.makeText(this, R.string.delete_success, Toast.LENGTH_SHORT).show();
            finish();
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
