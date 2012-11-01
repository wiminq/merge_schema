**Introduciton**

Compare and merge MySQL schemas.

**Note**

This script can't identify a rename action.

    -- e.g.:
    rename table test_table1 to test_table2;
    alter table test_table change c1 c2 int(10); 

**Samples**

	~/merge_schema (master) $ python merge_schema.py -f from_schema.sql -t to_schema.sql -o merge_alters.sql
    -- del_table
    drop table del_table;
     
    -- add_table
    CREATE TABLE `add_table` (
      `id` int(11) NOT NULL,
      `c1` int(11) DEFAULT NULL,
      `c2` int(11) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
     
    -- del_key
    alter table `del_key` drop key ind_c1;
     
    -- add_fulltext
    alter table `add_fulltext` add FULLTEXT KEY `ft_c1` (`c1`);
     
    -- del_column
    alter table `del_column` drop column `c3`;
     
    -- add_key
    alter table `add_key` add KEY `ind_c` (`c1`,`c2`);
     
    -- del_fulltext
    alter table `del_fulltext` drop fulltext key `ft_c1`;
     
    -- mod_option
    alter table `mod_option` ENGINE=BLACKHOLE DEFAULT CHARSET=utf8;
     
    -- add_primary
    alter table `add_primary` add PRIMARY KEY (`id`);
     
    -- mod_column
    alter table `mod_column` modify column `c1` char(16) DEFAULT NULL;
     
    -- mod_key
    alter table `mod_key` drop key ind_c;
    alter table `mod_key` add KEY `ind_c` (`c1`,`c2`);
     
    -- del_foreign
    alter table `del_foreign` drop foreign key `fk_id2`;
     
    -- add_unique
    alter table `add_unique` add UNIQUE KEY `unq_c1` (`c1`);
     
    -- mod_foreign
    alter table `mod_foreign` drop foreign key `fk_id1`;
    alter table `mod_foreign` add CONSTRAINT `fk_id1` FOREIGN KEY (`id`) REFERENCES `del_foreign` (`id`);
     
    -- mod_fulltext
    alter table `mod_fulltext` drop fulltext key `ft_c`;
    alter table `mod_fulltext` add FULLTEXT KEY `ft_c` (`c1`,`c2`);
     
    -- add_column
    alter table `add_column` add column ``c3` int(11) DEFAULT NULL`;
     
    -- del_unique
    alter table `del_unique` drop unique key unq_c1;
     
    -- del_primary
    alter table `del_primary` drop primary key;
     
    -- mod_unique
    alter table `mod_unique` drop unique key unq_c;
    alter table `mod_unique` add UNIQUE KEY `unq_c` (`c1`,`c2`);
     
    -- mod_primary
    alter table `mod_primary` drop primary key;
    alter table `mod_primary` add PRIMARY KEY (`id`,`c1`);
     
    -- add_foreign
    alter table `add_foreign` add CONSTRAINT `fk_id2` FOREIGN KEY (`id`) REFERENCES `del_foreign` (`id`);
     
