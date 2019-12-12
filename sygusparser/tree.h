
class cmd
{
public:
    virtual ~cmd() {}
};

class cmd_set_logic : public cmd
{
public:
    virtual ~cmd_set_logic() {}
};

class cmd_define_sort : public cmd
{
public:
    virtual ~cmd_define_sort() {}
};

class cmd_declare_var : public cmd
{
public:
    virtual ~cmd_declare_var() {}
};

class cmd_declare_fun : public cmd
{
public:
    virtual ~cmd_declare_fun() {}
};

class cmd_define_fun : public cmd
{
public:
    virtual ~cmd_define_fun() {}
};

class cmd_synth_fun : public cmd
{
public:
    virtual ~cmd_synth_fun() {}
};

class cmd_constraint : public cmd
{
public:
    virtual ~cmd_constraint() {}
};

class cmd_check_synth : public cmd
{
public:
    virtual ~cmd_check_synth() {}
};

class cmd_set_options : public cmd
{
public:
    virtual ~cmd_set_options() {}
};
